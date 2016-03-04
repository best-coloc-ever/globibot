from utils.logging import logger

from imghdr import what as image_type
from PIL import Image, ImageSequence

from urllib.request import urlretrieve
from collections import defaultdict
from subprocess import call
from tempfile import mkstemp, mkdtemp
from shutil import rmtree

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

    def register_emote(self, emote_name, size, url):
        if self.url_store[emote_name].get(size) is None:
            self.url_store[emote_name][size] = url

    def load_global(self):
        URL = 'http://twitchemotes.com/api_cache/v2/global.json'
        response = requests.get(URL)
        data = response.json()
        for emote_name, emote in data['emotes'].items():
            image_id = str(emote['image_id'])
            for size in EmoteStore.SIZES:
                url = data['template'][size].replace('{image_id}', image_id)
                self.register_emote(emote_name, size, url)

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
                    self.register_emote(code, size, url)

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
                self.register_emote(emote['code'], size, 'http:{}'.format(location))

        # Special BTTV
        URL = 'https://raw.githubusercontent.com/Jiiks/BetterDiscordApp/master/data/emotedata_bttv.json'
        response = requests.get(URL)
        for emote_name, emote_id in response.json().items():
            for size, bttv_size in zip(EmoteStore.SIZES, BTTV_SIZES):
                location = template.replace('{{id}}', emote_id)\
                                   .replace('{{image}}', bttv_size)
                self.register_emote(emote_name, size, 'http:{}'.format(location))

    def load_ffz(self):
        URL = 'https://raw.githubusercontent.com/Jiiks/BetterDiscordApp/master/data/emotedata_ffz.json'
        FFZ_SIZE = ['1', '2', '4'] # Weirdest shit
        response = requests.get(URL)
        for emote_name, emote_id in response.json().items():
            for size, ffz_size in zip(EmoteStore.SIZES, FFZ_SIZE):
                location = 'https://cdn.frankerfacez.com/emoticon/{}/{}'.format(emote_id, ffz_size)
                self.register_emote(emote_name, size, location)

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

    def assemble(self, emote_layout, size):
        emote_hash = '_'.join(map(lambda row: '-'.join(row), emote_layout))
        file_name = self.assembled_store[emote_hash].get(size)
        if file_name:
            return file_name

        emote_files = [
            [
                emote_file for emote_file in [
                    self.get(name, size) for name in emote_row
                ]
                if emote_file
            ] for emote_row in emote_layout
        ]

        images = [
            [
                Image.open(emote_file) for emote_file in emote_file_row
            ] for emote_file_row in emote_files
        ]

        images = [image for image in images if image]

        if images:
            max_width = max(map(lambda image_row: sum(map(lambda i: i.width, image_row)), images))
            total_height = sum(map(lambda image_row: max(map(lambda i: i.height, image_row)), images))


            images_frames = [
                [
                    [
                        frame.copy() for frame in ImageSequence.Iterator(image)
                    ] for image in row
                ] for row in images
            ]

            max_frames = 1
            for row in images_frames:
                for frames in row:
                    max_frames = max(max_frames, len(frames))

            max_frames = min(50, max_frames) # Limiting frames

            assembled = [
                Image.new('RGBA', (max_width, total_height))
                for i in range(max_frames)
            ]

            print('builing image...')
            y = 0
            for row in images_frames:
                x = 0
                for frames in row:
                    for i in range(max_frames):
                        assembled[i].paste(frames[i % len(frames)], (x, y))
                    x += frames[0].width
                y += max(map(lambda f: f[0].height, row))

            print('dump {}...'.format(max_frames))
            if max_frames == 1:
                file_name = '{}.png'.format(mkstemp()[1])
                assembled[0].save(file_name)
            else:
                d = mkdtemp()
                pngs = []
                for i, img in enumerate(assembled):
                    name = os.path.join(d, '{}.png'.format(i))
                    img.save(name)
                    pngs.append(name)
                print('convert...')
                file_name = '{}.gif'.format(mkstemp()[1])
                command = ['convert', '-delay', '5', '-dispose', 'previous', '-loop', '0', '-strip'] + pngs + [file_name]
                call(command)
                call(['du', '-sm', file_name])
                rmtree(d)

            self.assembled_store[emote_hash][size] = file_name

            return file_name
