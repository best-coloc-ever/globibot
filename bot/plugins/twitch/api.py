from tornado.escape import json_decode
from tornado.httputil import url_concat
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.platform.asyncio import to_asyncio_future

from collections import namedtuple

def unpack_value(k, v):
    if type(v) is dict:
        return struct_from_dict(k.title(), v)
    return v

def struct_from_dict(name, d):
    stripped_dict = dict([
        (k, unpack_value(k, v)) for k, v in d.items()
        if not k.startswith('_')
    ])

    return namedtuple(name, stripped_dict.keys())(*stripped_dict.values())

class TwitchAPI:

    BASE_URL = 'https://api.twitch.tv/kraken'

    OBJECT_BUILDER = lambda name: lambda d: struct_from_dict(name, d)

    def __init__(self, client_id, debug):
        self.client_id = client_id
        self.debug = debug

        self.client = AsyncHTTPClient()

    TOP_GAMES_ENDPOINT = '/games/top'
    TopGame = OBJECT_BUILDER('TopGame')
    async def top_games(self, count):
        json = await self.get_json(TwitchAPI.TOP_GAMES_ENDPOINT, dict(
            limit=min(count, 100)
        ))

        return list(map(TwitchAPI.TopGame, json['top']))

    STREAMS_ENDPOINT = '/streams'
    Stream = OBJECT_BUILDER('Stream')
    async def top_channels(self, count):
        json = await self.get_json(TwitchAPI.STREAMS_ENDPOINT, dict(
            limit=min(count, 100)
        ))

        return list(map(TwitchAPI.Stream, json['streams']))

    STREAM_ENDPOINT = lambda name: '{}/{}'.format(TwitchAPI.STREAMS_ENDPOINT, name)
    async def stream(self, name):
        json = await self.get_json(TwitchAPI.STREAM_ENDPOINT(name))

        stream = json['stream']
        if stream:
            return TwitchAPI.Stream(stream)

    CHANNEL_ENDPOINT = lambda name: '/channels/{}'.format(name)
    Channel = OBJECT_BUILDER('Channel')
    async def channel(self, name):
        json = await self.get_json(TwitchAPI.CHANNEL_ENDPOINT(name))

        return TwitchAPI.Channel(json)

    USER_ENDPOINT = '/user'
    USER_FOLLOWED_ENDPOINT = lambda user: '/users/{}/follows/channels'.format(user)
    Follow = OBJECT_BUILDER('Follow')
    async def user_followed(self, token):
        user = await self.get_json(TwitchAPI.USER_ENDPOINT, token=token)

        json = await self.get_json(
            TwitchAPI.USER_FOLLOWED_ENDPOINT(user['name']),
            params = dict(limit=100),
        )

        return list(map(TwitchAPI.Follow, json['follows']))

    async def get_json(self, endpoint, params={}, token=None):
        url = url_concat(TwitchAPI.BASE_URL + endpoint, params)
        request = HTTPRequest(
            url     = url,
            headers = self.api_headers(token)
        )
        tornado_future = self.client.fetch(request)
        future = to_asyncio_future(tornado_future)
        response = await future

        return json_decode(response.body)

    '''
    Details
    '''

    def api_headers(self, token):
        headers = {
            'Client-ID':     self.client_id,
        }
        if token:
            headers['Authorization'] = 'OAuth {}'.format(token)

        return headers
