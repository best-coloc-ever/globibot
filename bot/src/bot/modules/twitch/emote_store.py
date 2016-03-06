from utils.logging import logger

from tornado.httpclient import AsyncHTTPClient
from tornado.platform.asyncio import to_asyncio_future
from tornado.escape import json_decode

from imghdr import what as image_type
from PIL import Image, ImageSequence

from collections import defaultdict
from subprocess import call
from tempfile import mkstemp, mkdtemp
from shutil import rmtree

import asyncio
import os

class EmoteStore:

    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'

    SIZES = [SMALL, MEDIUM, LARGE]

    def __init__(self):
        self.url_store = defaultdict(dict)
        self.file_store = defaultdict(dict)
        self.assembled_store = defaultdict(dict)

        self.http_client = AsyncHTTPClient()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.load())

    def register_emote(self, emote_name, size, url):
        if self.url_store[emote_name].get(size) is None:
            self.url_store[emote_name][size] = url

    async def load(self):
        return await asyncio.gather(
            asyncio.ensure_future(self.load_global()),
            asyncio.ensure_future(self.load_subscriber()),
            asyncio.ensure_future(self.load_bttv()),
            asyncio.ensure_future(self.load_bttv2())
        )

    async def http_get(self, url):
        tornado_future = self.http_client.fetch(url)
        return await to_asyncio_future(tornado_future)

    async def load_global(self):
        URL = 'http://twitchemotes.com/api_cache/v2/global.json'
        response = await self.http_get(URL)
        data = json_decode(response.body)
        for emote_name, emote in data['emotes'].items():
            image_id = str(emote['image_id'])
            for size in EmoteStore.SIZES:
                url = data['template'][size].replace('{image_id}', image_id)
                self.register_emote(emote_name, size, url)

    async def load_subscriber(self):
        URL = 'http://twitchemotes.com/api_cache/v2/subscriber.json'
        response = await self.http_get(URL)
        data = json_decode(response.body)
        for channel in data['channels'].values():
            for emote in channel['emotes']:
                code = emote['code']
                image_id = str(emote['image_id'])
                for size in EmoteStore.SIZES:
                    url = data['template'][size].replace('{image_id}', image_id)
                    self.register_emote(code, size, url)

    async def load_bttv(self):
        URL = 'https://api.betterttv.net/2/emotes'
        BTTV_SIZES = ['1x', '2x', '3x']
        BTTV_TEMPLATE = "//cdn.betterttv.net/emote/{{id}}/{{image}}"
        response = await self.http_get(URL)
        data = json_decode(response.body)
        for emote in data['emotes']:
            for size, bttv_size in zip(EmoteStore.SIZES, BTTV_SIZES):
                location = BTTV_TEMPLATE.replace('{{id}}', emote['id'])\
                                   .replace('{{image}}', bttv_size)
                self.register_emote(emote['code'], size, 'http:{}'.format(location))

    async def load_bttv2(self):
        URL = 'https://raw.githubusercontent.com/Jiiks/BetterDiscordApp/master/data/emotedata_bttv.json'
        BTTV_SIZES = ['1x', '2x', '3x']
        BTTV_TEMPLATE = "//cdn.betterttv.net/emote/{{id}}/{{image}}"
        response = await self.http_get(URL)
        data = json_decode(response.body)
        for emote_name, emote_id in data.items():
            for size, bttv_size in zip(EmoteStore.SIZES, BTTV_SIZES):
                location = BTTV_TEMPLATE.replace('{{id}}', emote_id)\
                                   .replace('{{image}}', bttv_size)
                self.register_emote(emote_name, size, 'http:{}'.format(location))

    async def get(self, emote_name, size):
        # Already downloaded ?
        file_name = self.file_store[emote_name].get(size)
        if file_name:
            return file_name

        # Does is exist ?
        emote_url = self.url_store[emote_name].get(size)
        if emote_url is None:
            return None

        # Download it
        try:
            response = await self.http_get(emote_url)
        except Exception as e:
            logger.error('Failed to fetch "{}" on size {}: {}'.format(
                emote_name, size, e
            ))
            if size == EmoteStore.SMALL:
                self.file_store[emote_name][size] = None
                return None
            return await self.get(emote_name, EmoteStore.SMALL)

        # Save it
        _, temp_file = mkstemp()
        with open(temp_file, 'wb') as f:
            f.write(response.body)

        # Use the proper file extension for Discord to recognize the format
        ext = image_type(temp_file)
        file_name = '{}.{}'.format(temp_file, ext)
        os.rename(temp_file, file_name)

        self.file_store[emote_name][size] = file_name

        return file_name

    async def assemble(self, emote_layout, size):
        # Already downloaded ?
        emote_hash = '_'.join(map(lambda row: '-'.join(row), emote_layout))
        file_name = self.assembled_store[emote_hash].get(size)
        if file_name:
            return file_name

        # Prefetch images
        tasks = []
        for row in emote_layout:
            for emote in row:
                tasks.append(asyncio.ensure_future(self.get(emote, size)))

        await asyncio.gather(*tasks)

        # Build the canvas
        images = []
        max_width = 0
        total_height = 0
        max_frames = 1

        for row in emote_layout:
            width = 0
            max_height = 0
            image_row = []

            for emote in row:
                emote_file = await self.get(emote, size)

                if emote_file is None:
                    continue

                image = Image.open(emote_file)
                frames = [frame.copy() for frame in ImageSequence.Iterator(image)]

                width += image.width
                max_height = max(max_height, image.height)
                max_frames = max(max_frames, len(frames))

                image_row.append(frames)

            if image_row:
                images.append(image_row)

            max_width = max(max_width, width)
            total_height += max_height

        if images:

            assembled = []

            for i in range(max_frames):
                image = Image.new('RGBA', (max_width, total_height))

                y = 0
                for row in images:
                    x = 0
                    max_height = 0

                    for frames in row:
                        frame = frames[i % len(frames)]
                        image.paste(frame, (x, y))

                        x += frame.width
                        max_height = max(max_height, frame.height)

                    y += max_height

                assembled.append(image)

            _, file_name = mkstemp()

            if max_frames == 1:
                file_name = '{}.png'.format(file_name)
                assembled[0].save(file_name)
            else:
                d = mkdtemp()
                pngs = []
                for i, img in enumerate(assembled):
                    name = os.path.join(d, '{}.png'.format(i))
                    img.save(name)
                    pngs.append(name)
                file_name = '{}.gif'.format(file_name)
                command = ['convert', '-delay', '5', '-dispose', 'previous', '-loop', '0', '-strip'] + pngs + [file_name]
                call(command)
                call(['du', '-sm', file_name])
                rmtree(d)

            self.assembled_store[emote_hash][size] = file_name

            return file_name
