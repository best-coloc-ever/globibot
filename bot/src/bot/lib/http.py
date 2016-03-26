from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat
from tornado.platform.asyncio import to_asyncio_future

async def http_get(url, params={}):
    url = url_concat(url, params)
    client = AsyncHTTPClient()
    tornado_future = client.fetch(url)
    try:
        return await to_asyncio_future(tornado_future)
    except:
        return None
