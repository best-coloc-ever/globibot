import requests
from urllib.request import urlretrieve

from imghdr import what as image_type

from utils.logging import logger

from collections import defaultdict

import os

class EmoteStore:

    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'

    SIZES = [SMALL, MEDIUM, LARGE]

    def __init__(self):
        self.url_store = defaultdict(dict)
        self.file_store = defaultdict(dict)

        self.load_global()
        self.load_subscriber()
        self.load_bttv()

        logger.info('loaded {} twitch emotes'.format(len(self.url_store)))

    def load_global(self):
        response = requests.get('http://twitchemotes.com/api_cache/v2/global.json')
        data = response.json()
        for emote_name, emote in data['emotes'].items():
            image_id = str(emote['image_id'])
            for size in EmoteStore.SIZES:
                template = data['template'][size]
                self.url_store[emote_name][size] = template.replace('{image_id}', image_id)

    def load_subscriber(self):
        response = requests.get('http://twitchemotes.com/api_cache/v2/subscriber.json')
        data = response.json()
        for channel in data['channels'].values():
            for emote in channel['emotes']:
                code = emote['code']
                image_id = str(emote['image_id'])
                for size in EmoteStore.SIZES:
                    template = data['template'][size]
                    self.url_store[code][size] = template.replace('{image_id}', image_id)

    def load_bttv(self):
        BTTV_SIZES = ['1x', '2x', '3x']
        response = requests.get('https://api.betterttv.net/2/emotes')
        data = response.json()
        template = data['urlTemplate']
        for emote in data['emotes']:
            for size, bttv_size in zip(EmoteStore.SIZES, BTTV_SIZES):
                url = template.replace('{{id}}', emote['id']).replace('{{image}}', bttv_size)
                self.url_store[emote['code']][size] = 'http:{}'.format(url)

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
        temp_file, _ = urlretrieve(emote_url)
        ext = image_type(temp_file)
        file_name = '{}.{}'.format(temp_file, ext)
        os.rename(temp_file, file_name)
        self.file_store[emote_name][size] = file_name
        return file_name
