from utils.logging import logger

from imghdr import what as image_type
from PIL import Image

from urllib.request import urlretrieve
from collections import defaultdict
from tempfile import mkstemp

import requests
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

        self.load_global()
        self.load_subscriber()
        self.load_bttv()
        self.load_ffz()

    def load_global(self):
        URL = 'http://twitchemotes.com/api_cache/v2/global.json'
        response = requests.get(URL)
        data = response.json()
        for emote_name, emote in data['emotes'].items():
            image_id = str(emote['image_id'])
            for size in EmoteStore.SIZES:
                url = data['template'][size].replace('{image_id}', image_id)
                self.url_store[emote_name][size] = url

    def load_subscriber(self):
        URL = 'http://twitchemotes.com/api_cache/v2/subscriber.json'
        response = requests.get(URL)
        data = response.json()
        for channel in data['channels'].values():
            for emote in channel['emotes']:
                code = emote['code']
                image_id = str(emote['image_id'])
                for size in EmoteStore.SIZES:
                    url = data['template'][size].replace('{image_id}', image_id)
                    self.url_store[code][size] = url

    def load_bttv(self):
        URL = 'https://api.betterttv.net/2/emotes'
        BTTV_SIZES = ['1x', '2x', '3x']
        response = requests.get(URL)
        data = response.json()
        template = data['urlTemplate']
        for emote in data['emotes']:
            for size, bttv_size in zip(EmoteStore.SIZES, BTTV_SIZES):
                location = template.replace('{{id}}', emote['id'])\
                                   .replace('{{image}}', bttv_size)
                self.url_store[emote['code']][size] = 'http:{}'.format(location)

        # Special BTTV
        URL = 'https://raw.githubusercontent.com/Jiiks/BetterDiscordApp/master/data/emotedata_bttv.json'
        response = requests.get(URL)
        for emote_name, emote_id in response.json().items():
            for size, bttv_size in zip(EmoteStore.SIZES, BTTV_SIZES):
                location = template.replace('{{id}}', emote_id)\
                                   .replace('{{image}}', bttv_size)
                self.url_store[emote_name][size] = 'http:{}'.format(location)

    def load_ffz(self):
        URL = 'https://raw.githubusercontent.com/Jiiks/BetterDiscordApp/master/data/emotedata_ffz.json'
        FFZ_SIZE = ['1', '2', '4'] # Weirdest shit
        response = requests.get(URL)
        for emote_name, emote_id in response.json().items():
            for size, ffz_size in zip(EmoteStore.SIZES, FFZ_SIZE):
                location = 'https://cdn.frankerfacez.com/emoticon/{}/{}'.format(emote_id, ffz_size)
                self.url_store[emote_name][size] = location

    def get(self, emote_name, size):
        # Already downloaded ?
        file_name = self.file_store[emote_name].get(size)
        if file_name:
            return file_name

        # Does is exist ?
        emote_url = self.url_store[emote_name].get(size)
        if emote_url is None:
            return None

        # Download and save it
        try:
            temp_file, _ = urlretrieve(emote_url)
        except Exception as e:
            logger.error('Failed to fetch "{}" on size {}: {}'.format(
                emote_name, size, e
            ))
            if size == EmoteStore.SMALL:
                return None
            return self.get(emote_name, EmoteStore.SMALL)
        ext = image_type(temp_file)
        file_name = '{}.{}'.format(temp_file, ext)
        os.rename(temp_file, file_name)
        self.file_store[emote_name][size] = file_name

        return file_name

    def assemble(self, emotes, size):
        emote_hash = ''.join(emotes)
        file_name = self.assembled_store[emote_hash].get(size)
        if file_name:
            return file_name

        emote_files = [
            emote_file for emote_file in [
                self.get(name, size) for name in emotes
            ]
            if emote_file
        ]

        images = [Image.open(emote_file) for emote_file in emote_files]

        if images:
            total_width = sum(map(lambda i: i.width, images))
            max_height = max(map(lambda i: i.height, images))
            assembled = Image.new('RGBA', (total_width, max_height))

            x = 0
            for image in images:
                assembled.paste(image, (x, 0))
                x += image.width

            file_name = '{}.png'.format(mkstemp()[1])
            assembled.save(file_name)
            self.assembled_store[emote_hash][size] = file_name

            return file_name
