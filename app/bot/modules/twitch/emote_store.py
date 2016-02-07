import requests
from urllib.request import urlretrieve

from imghdr import what as image_type

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
