from tornado.escape import json_decode
from tornado.httputil import url_concat
from tornado.httpclient import AsyncHTTPClient
from tornado.platform.asyncio import to_asyncio_future

from collections import namedtuple
from datetime import datetime
from time import time as now

from asyncio import gather

CMC_API_PREFIX = 'https://api.coinmarketcap.com/v1'
EXCHANGES = set((
    "aud", "brl", "cad", "chf", "clp", "cny", "czk", "dkk", "eur", "gbp", "hkd",
    "huf", "idr", "ils", "inr", "jpy", "krw", "mxn", "myr", "nok", "nzd", "php",
    "pkr", "pln", "rub", "sek", "sgd", "thb", "try", "twd", "zar"
))

BINANCE_API_PREFIX = 'https://api.binance.com/api/v1'
BITTREX_API_PREFIX = 'https://bittrex.com/api/v2.0'
POLONIEX_API_PREFIX = 'https://poloniex.com/public'

BINANCE_CURRENCY_ENDPOINT = ('/exchangeInfo', dict())
BITTREX_CURRENCY_ENDPOINT = ('/pub/Markets/GetMarketSummaries', dict())
POLONIEX_CURRENCY_ENDPOINT = ('', dict(command='returnTicker'))

BINANCE_EXTRACT_COIN_PAIR = lambda data: (
    (symbol['baseAsset'], symbol['quoteAsset'])
    for symbol in data['symbols']
)
BITTREX_EXTRACT_COIN_PAIR = lambda data: (
    (market['MarketCurrency'], market['BaseCurrency'])
    for market in (
        result['Market']
        for result in data['result']
    )
)
POLONIEX_EXTRACT_COIN_PAIR = lambda data: (
    tuple(currency_pair.split('_')[::-1])
    for currency_pair in data
)

def interval_time(interval_str):
    UNIT_TIMES = dict(m=60, h=3600, d=24*3600, w=7*24*3600, M=30*24*3600)
    factor, unit = float(interval_str[:-1]), interval_str[-1]
    return factor * UNIT_TIMES[unit]

BINANCE_INTERVAL_STRINGS = (
    '1m', '3m', '5m', '15m', '30m',
    '1h', '2h', '4h', '6h', '8h', '12h',
    '1d', '3d', '1w',
    '1M',
)

BINANCE_INTERVALS = sorted((
    (interval_time(interval_str), interval_str)
    for interval_str in BINANCE_INTERVAL_STRINGS
), reverse=True)

BITTREX_INTERVALS = sorted((
    (60, 'oneMin'), (5 * 60, 'fiveMin'), (30 * 60, 'thirtyMin'),
    (3600, 'hour'), (24 * 3600, 'day'),
), reverse=True)

double = lambda x: (x, x)
POLONIEX_INTERVALS = sorted((
    double(300), double(900), double(1800),
    double(7200), double(14400),
    double(86400)
), reverse=True)

EXPECTED_CANDLES = 50

def interval_from_span(intervals, span):
    return next(
        interval_str
        for time, interval_str in intervals
        if span / time >= EXPECTED_CANDLES
    )

def binance_data_endpoint(quote, base, span):
    symbol = '{}{}'.format(quote, base)
    interval = interval_from_span(BINANCE_INTERVALS, span)

    return ('/klines', dict(
        symbol=symbol,
        interval=interval,
    ))

def bittrex_data_endpoint(quote, base, span):
    symbol = '{}-{}'.format(base, quote)
    interval = interval_from_span(BITTREX_INTERVALS, span)

    return ('/pub/market/GetTicks', dict(
        marketName=symbol,
        tickInterval=interval,
    ))

def poloniex_data_endpoint(quote, base, span):
    symbol = '{}_{}'.format(base, quote)
    interval = interval_from_span(POLONIEX_INTERVALS, span)

    return ('', dict(
        command='returnChartData',
        currencyPair=symbol,
        start=now() - span,
        end=now(),
        period=interval,
    ))

BINANCE_EXTRACT_CANDLE_DATA = lambda data: [
    [float(x) for x in tick[:5]]
    for tick in data
]

BITTREX_EXTRACT_CANDLE_DATA = lambda data: [
    [
        datetime.strptime(tick["T"], '%Y-%m-%dT%H:%M:%S').timestamp() * 1000,
        tick["O"], tick["H"], tick["L"], tick["C"]
    ]
    for tick in data['result']
]

POLONIEX_EXTRACT_CANDLE_DATA = lambda data: [
    [
        tick["date"] * 1000,
        tick["open"], tick["high"], tick["low"], tick["close"]
    ]
    for tick in data
]

BINANCE_GROUPINGS = [
    ['minute', [3, 5, 15, 30]],
    ['hour',   [1, 2, 4, 6, 12]],
    ['day',    [1, 3]],
    ['week',   [1]],
    ['month',  [1]]
]

BITTREX_GROUPINGS = [
    ['minute', [1, 5, 30]],
    ['hour',   [1]],
    ['day',    [1]],
]

POLONIEX_GROUPINGS = [
    ['minute', [5, 15, 30]],
    ['hour',   [2, 4]],
    ['day',    [1]],
]

Market = namedtuple('Market', [
    'name',
    'api_prefix',
    'currency_endpoint',
    'extract_coin_pair',
    'data_endpoint',
    'extract_candle_data',
    'candle_groupings'
])

class Markets:
    BINANCE = Market('Binance',
        BINANCE_API_PREFIX,
        BINANCE_CURRENCY_ENDPOINT,
        BINANCE_EXTRACT_COIN_PAIR,
        binance_data_endpoint,
        BINANCE_EXTRACT_CANDLE_DATA,
        BINANCE_GROUPINGS,
    )
    BITTREX = Market('Bittrex',
        BITTREX_API_PREFIX,
        BITTREX_CURRENCY_ENDPOINT,
        BITTREX_EXTRACT_COIN_PAIR,
        bittrex_data_endpoint,
        BITTREX_EXTRACT_CANDLE_DATA,
        BITTREX_GROUPINGS,
    )
    POLONIEX = Market('Poloniex',
        POLONIEX_API_PREFIX,
        POLONIEX_CURRENCY_ENDPOINT,
        POLONIEX_EXTRACT_COIN_PAIR,
        poloniex_data_endpoint,
        POLONIEX_EXTRACT_CANDLE_DATA,
        POLONIEX_GROUPINGS
    )

ALL_MARKETS = (
    Markets.POLONIEX,
    Markets.BINANCE,
    Markets.BITTREX,
)

class CryptoApi:

    def __init__(self):
        self.client = AsyncHTTPClient()

    async def fetch(self, prefix, path, params):
        url = url_concat(prefix + path, params)
        print(url)
        tornado_future = self.client.fetch(url)
        future = to_asyncio_future(tornado_future)
        response = await future

        return json_decode(response.body)

    async def all_tickers(self, limit=0):
        ALL_TICKERS_PATH = '/ticker'

        return await self.fetch(
            CMC_API_PREFIX,
            ALL_TICKERS_PATH,
            params=dict(limit=limit)
        )

    async def ticker(self, currency_id, convert=None):
        TICKER_PATH = lambda id_: '/ticker/{}'.format(id_)

        params = dict() if convert is None else dict(convert=convert)
        return await self.fetch(
            CMC_API_PREFIX,
            TICKER_PATH(currency_id),
            params
        )

    async def currency_list(self, market):
        path, params = market.currency_endpoint
        data = await self.fetch(market.api_prefix, path, params)

        coin_pairs = market.extract_coin_pair(data)
        return dict(
            (coin_pair, market)
            for coin_pair in coin_pairs
        )

    async def markets_per_coin_pairs(self):
        list_currencies_tasks = (
            self.currency_list(market)
            for market in ALL_MARKETS
        )

        currency_lists = await gather(*list_currencies_tasks)

        all_markets_per_coin_pairs = dict()
        for currency_list in currency_lists:
            all_markets_per_coin_pairs.update(currency_list)

        return all_markets_per_coin_pairs

    async def candle_data(self, market, quote, base, span):
        path, params = market.data_endpoint(quote, base, span)

        raw_data = await self.fetch(market.api_prefix, path, params)

        return market.extract_candle_data(raw_data)

