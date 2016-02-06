import requests
from urllib.request import urlretrieve

from imghdr import what as image_type

from utils.logging import logger

import os

class EmoteStore:

    def __init__(self):
        self.url_store = {}
        self.file_store = {}

        self.load_global()
        self.load_subscriber()
        self.load_bttv()

        logger.info('loaded {} twitch emotes'.format(len(self.url_store)))

    def load_global(self):
        response = requests.get('http://twitchemotes.com/api_cache/v2/global.json')
        data = response.json()
        template = data['template']['medium']
        for emote_name, emote in data['emotes'].items():
            image_id = str(emote['image_id'])
            self.url_store[emote_name] = template.replace('{image_id}', image_id)

    def load_subscriber(self):
        response = requests.get('http://twitchemotes.com/api_cache/v2/subscriber.json')
        data = response.json()
        template = data['template']['medium']
        for channel in data['channels'].values():
            for emote in channel['emotes']:
                code = emote['code']
                image_id = str(emote['image_id'])
                self.url_store[code] = template.replace('{image_id}', image_id)

    def load_bttv(self):
        response = requests.get('https://api.betterttv.net/2/emotes')
        data = response.json()
        template = data['urlTemplate']
        for emote in data['emotes']:
            self.url_store[emote['code']] = template.replace('{{id}}', emote['id']).replace('{{image}}', '2x')

    def get(self, emote_name):
        # Already downloaded ?
        file_name = self.file_store.get(emote_name)
        if file_name:
            return file_name

        # Does is exist ?
        emote_url = self.url_store.get(emote_name)
        if emote_url is None:
            return None

        # Download and save it
        temp_file, _ = urlretrieve('http:{}'.format(emote_url))
        ext = image_type(temp_file)
        file_name = '{}.{}'.format(temp_file, ext)
        os.rename(temp_file, file_name)
        self.file_store[emote_name] = file_name
        return file_name
