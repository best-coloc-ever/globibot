from collections import namedtuple
from functools import partial

# import tweepy
import twitter
import asyncio

Credentials = namedtuple('Credentials', [
    'consumer_key', 'consumer_secret',
    'access_token', 'access_token_secret'
])

# class TwitterApi:

#     def __init__(self, credentials):
#         auth = tweepy.OAuthHandler(
#             credentials.consumer_key,
#             credentials.consumer_secret,
#         )
#         auth.set_access_token(
#             credentials.access_token,
#             credentials.access_token_secret,
#         )

#         self._client = tweepy.API(auth)

#     def __getattr__(self, attr):
#         method = getattr(self._client, attr)
#         return partial(self._async_call, method)

#     async def _async_call(self, method, *args, **kwargs):
#         loop = asyncio.get_event_loop()
#         sync_call = partial(method, *args, **kwargs)
#         result = await loop.run_in_executor(None, sync_call)
#         return result

class PartialExecutor:

    def __init__(self, partial):
        self.partial = partial

    async def __call__(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        sync_call = partial(self.partial, *args, **kwargs)
        return await loop.run_in_executor(None, sync_call)

    def __getattr__(self, attr_name):
        attr = getattr(self.partial, attr_name)
        return PartialExecutor(attr)

class TwitterApi:

    def __init__(self, credentials):
        self._auth = twitter.OAuth(
            credentials.access_token,
            credentials.access_token_secret,
            credentials.consumer_key,
            credentials.consumer_secret,
        )

        self._client = twitter.Twitter(auth=self._auth)

    def __getattr__(self, attr_name):
        attr = getattr(self._client, attr_name)
        return PartialExecutor(attr)
