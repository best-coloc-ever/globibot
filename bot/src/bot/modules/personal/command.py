from bot.lib.http import http_get

from .errors import FetchError, NotAnImageError

from . import constants as c

from tornado.escape import json_decode
from PIL import Image

from time import time
from io import BytesIO

import asyncio
import random

class Command:

    def __init__(self, prefix):
        self.prefix = prefix
        self.created_at = time()
        self.called_at = 0

    async def call(self, module, message):
        now = time()
        if now - self.called_at >= c.USAGE_COOLDOWN:
            await self.call_impl(module, message)
            self.called_at = now

class ImagesCommand(Command):

    async def initialize(self, urls):
        self.files = []

        responses = await asyncio.gather(
            *[http_get(url) for url in urls]
        )

        for i, response in enumerate(responses):
            if response is None:
                raise FetchError(urls[i])

            file_name = '/tmp/{}_{}.png'.format(self.prefix, i)

            try:
                image = Image.open(BytesIO(response.body))
            except:
                raise NotAnImageError(urls[i])
            image.save(file_name)

            self.files.append(file_name)

    async def call_impl(self, module, message):
        file_name = random.choice(self.files)
        await module.send_file(message.channel, file_name)

class GoogleCommand(Command):

    SEARCH_URL = 'https://www.googleapis.com/customsearch/v1'

    async def initialize(self, theme, api_key, cx):
        self.theme = theme
        self.api_key = api_key
        self.cx = cx

    async def call_impl(self, module, message):
        response = await http_get(GoogleCommand.SEARCH_URL, {
            'q': self.theme,
            'key': self.api_key,
            'cx': self.cx,
            'searchType': 'image',
            'imgSize': 'large',
            'num': 1,
            'safe': 'medium',
            'start': random.randint(0, 100)
        })

        if response is None:
            return

        data = json_decode(response.body)
        items = data['items']
        links = [item['link'] for item in items]

        if not links:
            return

        link = links[0]
        image_response = await http_get(link)
        try:
            image = Image.open(BytesIO(image_response.body))
        except:
            return

        file_name = '/tmp/{}.png'.format(self.prefix)
        image.save(file_name)

        await module.send_file(
            message.channel,
            file_name,
            'A random pic of `{}` from Google, courtesy of {}'
                .format(self.theme, message.author.mention)
        )

class YoutubeCommand(Command):

    SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

    async def initialize(self, theme, api_key):
        self.theme = theme
        self.api_key = api_key

    async def call_impl(self, module, message):
        response = await http_get(YoutubeCommand.SEARCH_URL, {
            'q': self.theme,
            'key': self.api_key,
            'part': 'snippet',
            'maxResults': 50,
        })

        if response is None:
            return

        data = json_decode(response.body)
        items = data['items']

        if not items:
            return

        item = random.choice(items)
        video_id = item['id']['videoId']

        await module.send_message(
            message.channel,
            'Here is a random video of `{}`, courtesy of {}:'
            'http://youtube.com/watch?v={}'
                .format(self.theme, message.author.mention, video_id)
        )
