from tornado.escape import json_decode
from tornado.httputil import url_concat
from tornado.httpclient import AsyncHTTPClient
from tornado.platform.asyncio import to_asyncio_future

class StocksApi:

    def __init__(self, key):
        self.client = AsyncHTTPClient()
        self.key = key

    async def fetch(self, path, params):
        params['apikey'] = self.key
        url = url_concat(f'https://www.alphavantage.co/{path}', params)
        tornado_future = self.client.fetch(url)
        future = to_asyncio_future(tornado_future)
        response = await future

        return json_decode(response.body)

    async def fetch_symbol_intraday(self, symbol):
        return await self.fetch('query', {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': '1min',
        })
