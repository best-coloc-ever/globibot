from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import master_only

from .api import CryptoApi, EXCHANGES
from .chart import make_chart

from traceback import format_exc
from time import time

from discord import Embed

import asyncio

SYMBOLS = {
    'eur': '€',
}

UNIT_TIMES = dict(h=3600, d=24*3600, w=7*24*3600, m=30*24*3600, y=365*3600)

SPAN_UNIT = p.one_of(p.a, 'h', 'd', 'w', 'm', 'y') >> p.to_s

def format_price(ticker, exchange):
    name, symbol = ticker['name'], ticker['symbol']
    change_1h = float(ticker.get('percent_change_1h', 0))
    change_24h = float(ticker.get('percent_change_24h', 0))
    change_7d = float(ticker.get('percent_change_7d', 0))

    exchanges = list()

    if exchange is not None:
        exchanges.append((exchange.upper(), ticker['price_{}'.format(exchange.lower())]))
    exchanges.append(('USD', ticker['price_usd']))
    if symbol != 'BTC':
        btc_price = float(ticker['price_btc'])
        btc_price_string = '{} (1 BTC ~= {:.3f} {})'.format(
            btc_price, 1 / btc_price, symbol)
        exchanges.append(('BTC', btc_price_string))

    price_message = '\n'.join(
        '{} :: {}'.format(exchange, value)
        for exchange, value in exchanges
    )

    changes = (change_1h, change_24h, change_7d)
    periods = ('hour',    'day',      'week')
    change_message = '\n'.join(
        '{} {:<{}} % over the last {}'.format(
            '-' if change < 0 else '+',
            abs(change), max(map(lambda x: len(str(abs(x))), changes)),
            period
        )
        for change, period in zip(changes, periods)
    )

    reply_message = '{} ({})\n{}\n{}\n{}\n{}'.format(
        name, symbol,
        '=' * (len(name) + len(symbol) + 3),
        price_message,
        '_' * (len(name) + len(symbol) + 3),
        change_message
    )

    last_updated_stamp = int(ticker['last_updated'])
    time_diff = int(time()) - last_updated_stamp
    if time_diff < 60:
        last_updated = '{} second{} ago'.format(time_diff, 's' if time_diff != 1 else '')
    else:
        minute_diff = time_diff // 60
        last_updated = '~{} minute{} ago'.format(minute_diff, 's' if minute_diff != 1 else '')

    return (
        '{}\n*last updated: {}*'
            .format(
                f.code_block(reply_message, language='asciidoc'),
                last_updated
            )
    )

def price_embed(ticker, exchange):
    name, symbol = ticker['name'], ticker['symbol']
    change_1h = float(ticker.get('percent_change_1h', 0))
    change_24h = float(ticker.get('percent_change_24h', 0))
    change_7d = float(ticker.get('percent_change_7d', 0))

    exchanges = list()

    if exchange is not None:
        price = float(ticker['price_{}'.format(exchange.lower())])
        exchanges.append((exchange.upper(), price))

    exchanges.append(('$', float(ticker['price_usd'])))

    if symbol != 'BTC':
        btc_price = float(ticker['price_btc'])
        exchanges.append(('฿', btc_price))

    price_message = '\n'.join(
        '{:.8f} {}'.format(value, SYMBOLS.get(exchange.lower(), exchange))
        for exchange, value in exchanges
    )

    changes = (change_1h, change_24h, change_7d)
    periods = ('h',       'd',        'w')
    change_message = '\n'.join(
        '**{}** {:} % (1{})'.format(
            '-' if change < 0 else '+',
            abs(change),
            period
        )
        for change, period in zip(changes, periods)
    )

    last_updated_stamp = int(ticker['last_updated'])
    time_diff = int(time()) - last_updated_stamp
    if time_diff < 60:
        last_updated = '{} second{} ago'.format(time_diff, 's' if time_diff != 1 else '')
    else:
        minute_diff = time_diff // 60
        last_updated = '~{} minute{} ago'.format(minute_diff, 's' if minute_diff != 1 else '')

    embed = Embed(
        title = '{} ({})'.format(name, symbol),
        description = '{}\n\n{}'.format(price_message, change_message),
        url = 'https://coinmarketcap.com/currencies/{}'.format(ticker['id'])
    )

    thumb_url = 'https://files.coinmarketcap.com/static/img/coins/32x32/{}.png'.format(ticker['id'])
    embed.set_thumbnail(url=thumb_url)

    embed.set_footer(text=last_updated)

    return embed

class CryptoCurrency(Plugin):

    def load(self):
        self.api = CryptoApi()
        self.currencies = dict()
        self.markets_per_coin_pairs = dict()

        self.run_async(self.fetch_all_currencies())
        self.run_async(self.fetch_market_coin_pairs())

    async def fetch_all_currencies(self):
        all_tickers = await self.api.all_tickers()

        for ticker in all_tickers:
            id_, name, symbol = ticker['id'], ticker['name'], ticker['symbol']
            self.currencies[name.lower()] = id_
            self.currencies[symbol.lower()] = id_
            self.currencies[id_.lower()] = id_

    async def fetch_market_coin_pairs(self):
        while True:
            self.markets_per_coin_pairs = await self.api.markets_per_coin_pairs()
            await asyncio.sleep(12 * 3600)

    @command(p.string('!price-old') + p.bind(p.word, 'currency')
                                    + p.bind(p.maybe(p.word), 'exchange'))
    async def crypto(self, message, currency, exchange=None):
        if currency.lower() not in self.currencies:
            await self.send_message(
                message.channel,
                '{} I did not find any cryptocurrency named **{}**'
                    .format(message.author.mention, currency)
            )
        elif exchange is not None and exchange.lower() not in EXCHANGES:
            await self.send_message(
                message.channel,
                '{} I cannot convert to **{}**'
                    .format(message.author.mention, exchange)
            )
        else:
            currency_id = self.currencies[currency.lower()]
            exchange = exchange.lower() if exchange is not None else None

            try:
                tickers = await self.api.ticker(currency_id, exchange)
                ticker = tickers[0]
            except:
                await self.send_message(
                    message.channel,
                    '{} there was an error contacting __coinmarketcap__'
                        .format(message.author.mention)
                )
            else:
                await self.send_message(
                    message.channel,
                    format_price(ticker, exchange)
                )

    @command(p.string('!price') + p.bind(p.word, 'currency')
                                + p.bind(p.maybe(p.word), 'exchange'))
    async def crypto(self, message, currency, exchange='EUR'):
        if currency.lower() not in self.currencies:
            await self.send_message(
                message.channel,
                '{} I did not find any cryptocurrency named **{}**'
                    .format(message.author.mention, currency)
            )
        elif exchange is not None and exchange.lower() not in EXCHANGES:
            await self.send_message(
                message.channel,
                '{} I cannot convert to **{}**'
                    .format(message.author.mention, exchange)
            )
        else:
            currency_id = self.currencies[currency.lower()]
            exchange = exchange.lower() if exchange is not None else None

            try:
                tickers = await self.api.ticker(currency_id, exchange)
                ticker = tickers[0]
            except:
                await self.send_message(
                    message.channel,
                    '{} there was an error contacting __coinmarketcap__'
                        .format(message.author.mention)
                )
            else:
                await self.send_message(
                    message.channel,
                    '',
                    embed=price_embed(ticker, exchange)
                )

    @command(p.string('!chart') + p.bind(p.word, 'quote')
                                + p.bind(p.word, 'base')
                                + p.bind(p.integer, 'span_factor')
                                + p.bind(SPAN_UNIT, 'span_unit'))
    async def chart(self, message, quote, base, span_factor, span_unit):
        quote = quote.upper()
        base = base.upper()
        span = span_factor * UNIT_TIMES[span_unit]

        m = await self.send_message(
            message.channel,
            'Generating the chart...'
        )

        try:
            true_base = 'BTC' if base == 'USD' else base
            market = self.markets_per_coin_pairs[(quote, true_base)]
        except KeyError:
            await self.send_message(
                message.channel,
                'I don\'t aggregate any market that has that data'
            )
        else:
            try:
                data = await self.api.candle_data(market, quote, true_base, span)
            except Exception as e:
                self.error(format_exc(e))
                await self.send_message(
                    message.channel,
                    'Error fetching data from {}'.format(market.name)
                )
            else:
                try:
                    if base == 'USD':
                        tickers = await self.api.ticker(self.currencies['btc'], None)
                        ticker = tickers[0]
                        price = float(ticker['price_usd'])
                        data = [
                            [i[0], *(x * price for x in i[1:])]
                            for i in data
                        ]
                except Exception as e:
                    self.error(format_exc(e))
                    await self.send_message(
                        message.channel,
                        'Error converting BTC to USD'
                    )
                chart = make_chart(quote, base, market, span_factor, span_unit, data)
                await self.send_file(
                    message.channel,
                    chart
                )
        finally:
            await self.bot.delete_message(m)
