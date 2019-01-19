from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command
from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import global_cooldown, user_cooldown, master_only

from tornado.escape import json_decode
from tornado.httputil import url_concat
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.platform.asyncio import to_asyncio_future

import json
import asyncio
import tempfile
import pytesseract

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from discord import Embed

from urllib.parse import urlencode

from random import randint, choice, shuffle
from collections import defaultdict

from time import time

from urllib.parse import urlencode, quote

from io import BytesIO

import os
import re
import datetime
import calendar

from .data import PJS, FIGHT_TEXTS, RATE_REACTIONS, GENERAL_DESCRIPTION, \
    POLL_EMOTES
from .handlers import ToxicityTableHandler, ToxicityDataHandler, AnimalsDataHandler, AnimalsViewHandler

from collections import namedtuple

from itertools import cycle

RE_EMOJI = re.compile('<a?:\S+:[0-9]+>')
RE_MENTION = re.compile('<@!?[0-9]+>')

LIRIK_ID = '98589509347704832'
LIRIK_SERVER_ID = '84822922958487552'
LIRIK_GENERAL = '84822922958487552'

RATE_FIXED = {
    # Globi
    '89108411861467136': 9,
    # # Marcus
    # '98469036936945664': 10,
    # # Alex
    # '129311731691290624': 0,
    # Rad
    '201745910420602880': 1,
}

AUTISM_SCAN_ALLOWED_USERS = (
    '89108411861467136',
    '86275464422789120'
)

REGIONAL_INDICATORS = {
    'a' : "🇦", 'b' : "🇧", 'c' : "🇨", 'd' : "🇩", 'e' : "🇪", 'f' : "🇫",
    'g' : "🇬", 'h' : "🇭", 'i' : "🇮", 'j' : "🇯", 'k' : "🇰", 'l' : "🇱",
    'm' : "🇲", 'n' : "🇳", 'o' : "🇴", 'p' : "🇵", 'q' : "🇶", 'r' : "🇷",
    's' : "🇸", 't' : "🇹", 'u' : "🇺", 'v' : "🇻", 'w' : "🇼", 'x' : "🇽",
    'y' : "🇾", 'z' : "🇿",
}

FLAGS_PER_LANG = {
    'sv': '🇸🇪',
    # 'iw': '🇮🇱',
    'iw': '🇵🇸',
    'ar': '🇵🇸',
    'da': '🇩🇰',
    'ga': '🇮🇪',
    'nl': '♿',
    'lb': '🇱🇺'
}

PET_OWNERS = {
    'peach': 'peach',
    'nola': 'nola',
    'alphaca': 'alphacas',
    'alpaca': 'alphacas',
    'trico': 'trico',
    'leon': 'leon',
    'minxy': 'minxy',
    'baldcat': 'loki',
    'pickles': 'pickles',
    'gingerbois': 'becca',
    'ciri': 'ciri',
    'triss': 'triss',
    'maja': 'wito',
    'pawson': 'pawson',
    'harvey': 'harvey',
    'ezio': 'ezio',
}

DAB_EMOJI_NAMES = (
    'botdab',
    'botmoon2dab',
    'botmoon2rdab',
    'botrobdab',
    'botbitchdab',
)

def is_link(word):
    return word.startswith('http://') or word.startswith('https://')

class AnimalCollage:

    def __init__(self):
        self.http_client = AsyncHTTPClient(
            request_timeout=3,
            connect_timeout=3,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
        )

    async def fetch_image(self, url):
        tornado_future = self.http_client.fetch(url)
        future = to_asyncio_future(tornado_future)
        response = await future

        return Image.open(BytesIO(response.body))

    async def create(self, images):
        canvas = Image.new('RGBA', (900, 1200), (255, 0, 0, 0))

        for x in range(3):
            for y in range(3):
                img = images[x * 3 + y]
                img.thumbnail((300, 400), Image.ANTIALIAS)
                canvas.paste(img, (x * 300, y * 400))

        _, path = tempfile.mkstemp('.png')
        canvas.save(path)

        return path


async def async_map(coro, iterable):
    return await asyncio.gather(*(coro(param) for param in iterable))

AnimalGalore = namedtuple('AnimalGalore', ['pet_owner_id', 'file_name', 'urls'])

class Lirik(Plugin):

    def load(self):
        self.handlers = dict(
            on_member_join   = self.on_member_join
        )

        self.server = self.bot.find_server(LIRIK_SERVER_ID)

        self.channel = next(
            channel for channel in self.server.channels
            if channel.id == LIRIK_GENERAL
        )

        self.last_game = None
        self.last_fights = list()

        self.fights = {
            'random': self.random_fight,
            'maffs': self.maffs_fight,
            'animals': self.redirect_to_trivia,
            'flags': self.redirect_to_trivia,
            'traps': self.redirect_to_trivia,
            'pokemons': self.redirect_to_trivia,
            'capitals': self.redirect_to_trivia,
        }

        self.http_client = AsyncHTTPClient()

        try:
            with open('/tmp/globibot/frowns', 'r') as f:
                self.frown_faces = json.load(f)
        except Exception as e:
            self.warning('frowns... {}'.format(e))
        self.frown_count, ms = self.compute_frown_count()
        self.debug('{} frowns in {} messages'.format(self.frown_count, ms))

        try:
            with open('/tmp/globibot/flags.json', 'r') as f:
                self.flags = json.load(f)
        except Exception as e:
            self.debug('NO FLAGS :(((, {}'.format(e))

        try:
            with open('/tmp/globibot/complaints', 'r') as f:
                self.complaints = int(f.read())
        except Exception as e:
            self.complaints = 0

        def channel(id):
            return next(
                channel for channel in self.server.channels
                if channel.id == id
            )

        async def test():
            pass

        self.gophers = [
            (f[:-4].lower(), os.path.join(dp, f))
            for path in (
                '/tmp/globibot/gophers',
                '/tmp/globibot/other_gophers/sketch',
            )
            for dp, _, fn in os.walk(path)
            for f in fn
            if f[-4:].lower() == '.png' or f[-4:].lower() == '.jpg'
        ]

        def galore_spec(user_id, file_name):
            with open(f'/tmp/globibot/animals_galore/{file_name}', 'r') as f:
                urls = json.load(f)
                shuffle(urls)
                return AnimalGalore(user_id, file_name, cycle(urls))

        self.animal_galore = {
            'peach':    galore_spec('157555104197771264', 'peach.json'),
            'nola':     galore_spec('157555104197771264', 'nola.json'),
            'alphacas': galore_spec('449607034917093379', 'alphacas.json'),
            'trico':    galore_spec('449607034917093379', 'trico.json'),
            'leon':     galore_spec('449607034917093379', 'leon.json'),
            'minxy':    galore_spec('141815615441600513', 'minxy.json'),
            'loki':     galore_spec('98468779041763328',  'loki.json'),
            'pickles':  galore_spec('126036969791815681', 'pickles.json'),
            'becca':    galore_spec('128613961829449728', 'becca.json'),
            'ciri':     galore_spec('107400135952093184', 'ciri.json'),
            'triss':    galore_spec('107400135952093184', 'triss.json'),
            'wito':     galore_spec('82988997365731328',  'wito.json'),
            'pawson':   galore_spec('126487183916793856', 'pawson.json'),
            'harvey':   galore_spec('153392337337319424', 'harvey.json'),
            'ezio':     galore_spec('129314603162140673', 'ezio.json')
        }

        self.animals_collage = AnimalCollage()

        self.run_async(test())

        self.toxicity = self.load_toxicity()
        self.run_async(self.save_toxicity_periodically())

        context = dict(plugin=self)
        self.add_web_handlers(
            (r'/toxicity/table', ToxicityTableHandler, context),
            (r'/toxicity/data.json', ToxicityDataHandler, context),
            (r'/animals/data.json', AnimalsDataHandler, context),
            (r'/animals/all', AnimalsViewHandler, context),
        )

        GLOBIBOT_SERVER_ID = '143032611814637568'
        globibot_server = self.bot.find_server(GLOBIBOT_SERVER_ID)
        self.hide_link_emoji = next(
            emoji for emoji in globibot_server.emojis
            if emoji.name == 'hideLink'
        )
        self.processing_emoji = next(
            emoji for emoji in globibot_server.emojis
            if emoji.name == 'processing'
        )
        self.dab_emojis = cycle(
            next(
                emoji for emoji in globibot_server.emojis
                if emoji.name == emoji_name
            )
            for emoji_name in DAB_EMOJI_NAMES
        )

        self.last_pepo = 0

        self.wheelchair_counter = 0

        find_wc_users = '''
            select distinct author_id from log where channel_id = 462629869474283521
        '''

        with self.transaction() as trans:
            trans.execute(find_wc_users, dict())
            results = trans.fetchall()
            self.wc_speakers = set(str(r[0]) for r in results)
            self.wc_speakers.remove('89108411861467136')

        self.dab_ons = set()

    def unload(self):
        pass

    def load_toxicity(self):
        try:
            with open('/tmp/globibot/toxicity.json', 'r') as f:
                return json.load(f)
        except:
            return dict()

    def save_toxicity(self):
        try:
            with open('/tmp/globibot/toxicity.json', 'w') as f:
                json.dump(self.toxicity, f)
        except:
            pass

    async def save_toxicity_periodically(self):
        while True:
            self.save_toxicity()
            await asyncio.sleep(120)

    async def add_toxicity_sample(self, message):
        text = re.sub(RE_EMOJI, '', message.clean_content)

        if not text:
            return

        url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=AIzaSyDUQwNRONRAgf7NsSt70jv0PPL_X0WOXsA'
        keys = (
            'attack_on_author', 'attack_on_commenter', 'incoherent', 'inflammatory',
            'likely_to_reject', 'obscene', 'severe_toxicity', 'spam',
            'toxicity', 'unsubstantial',
        )
        body = {
            'comment': { 'text': text },
            'languages': ["en"],
            'requestedAttributes': {
                key.upper(): { }
                for key in keys
            },
        }

        tornado_future = self.http_client.fetch(
            url,
            body=json.dumps(body),
            method='POST',
            headers={ 'Content-Type': 'application/json' }
        )
        future = to_asyncio_future(tornado_future)
        response = await future

        data = json_decode(response.body.decode('utf8'))

        attributes = {
            key: data['attributeScores'][key.upper()]['summaryScore']['value']
            for key in keys
        }

        previous_attributes, message_count = self.toxicity.get(
            message.author.id,
            (defaultdict(lambda: 0), 0)
        )

        new_attributes = {
            key: (previous_attributes[key] * message_count + attributes[key]) / (message_count + 1)
            for key in keys
        }

        self.toxicity[message.author.id] = (new_attributes, message_count + 1)

    @command(p.string('!pet') + p.string('collage') + p.bind(p.maybe(p.word), 'pet'), global_cooldown(120, True))
    async def pet_collage(self, message, pet=None):
        if pet is not None:
            pet = pet.lower()

        if pet not in PET_OWNERS:
            pet_names = ' '.join(f'__{pet}__' for pet in PET_OWNERS.keys())
            await self.send_message(
                message.channel,
                f'__{pet}__ is not a know pet. Valid pet names are: {pet_names}.\nGenerating a random collage instead'
            )

        def pick_pet_image_url():
            try:
                owner = PET_OWNERS[pet]
            except KeyError:
                owner = choice(list(self.animal_galore.keys()))
            return next(self.animal_galore[owner].urls)

        await self.bot.add_reaction(message, self.processing_emoji)

        images = []
        retries = 0
        while len(images) < 9:
            image_url = pick_pet_image_url()
            try:
                image = await self.animals_collage.fetch_image(image_url)
            except Exception as e:
                self.error(f'Error fetching {image_url}: {e}')
                retries += 1
                if retries > 5:
                    await self.bot.clear_reactions(message)
                    await self.bot.add_reaction(message, '❌')
                    return
                await asyncio.sleep(1)
            else:
                images.append(image)
                await asyncio.sleep(0.5)

        collage_file = await self.animals_collage.create(images)

        await self.send_file(message.channel, collage_file)
        await self.bot.clear_reactions(message)


    @command(p.string('!random'), global_cooldown(60, True))
    async def random_cmd(self, message):
        command = choice([
            self.general, self.bg, self.unblock_all, self.faze, self.vp,
            self.c9, self.mimsy, self.ichi, self.diehard, self.galaxy,
            self.isis, self.dutch, self.jj, self.patent, self.binoculars,
            self.toolbox, self.jason, self.vic, self.dopamine, self.marcus,
            self.drge, self.jeff, self.peach, self.peachn,
            self.gingerbois, self.minxy, self.reno, self.alphaca,
            self.drree, self.disco, self.fluffeh, self.ghostfr, self.baldcat,
            self.rateme,
        ])

        await command(message)

    @command(
        p.string('!toxicity') + p.bind(p.mention, 'user'),
        global_cooldown(120, True)
    )
    async def user_toxicity(self, message, user):
        # try:
        #     attributes, message_count = self.toxicity[str(user)]
        # except KeyError:
        #     text = f'{f.mention(user)} has no history'
        # else:
        #     stats = f.code_block('\n'.join(
        #         f'{key:20} {attributes[key] * 100:.2f}%'
        #         for key in attributes.keys()
        #     ))
        #     text = f'averages for {f.mention(user)} ({message_count} messages):\n{stats}'

        # await self.send_message(message.channel, text)
        await self.send_message(message.channel, 'https://globibot.com/bot/toxicity/table')

    async def on_raw_event(self, event, *args, **kwargs):
        try:
            handler = self.handlers[event]
            await handler(*args, **kwargs)
        except KeyError:
            pass

    @command(p.string('!easter'), master_only)
    async def someone(self, message):
        new_line = '\n'
        await self.bot.delete_message(message)
        await self.send_message(
            message.channel,
            f'**@someone** \n{message.content[8:]}'
        )

    @command(p.string('!<>') + p.bind(p.mention, 'user'), master_only)
    async def quotify(self, message, user):
        last_m = next(
            m for m in
            reversed(self.bot.messages)
            if m.channel == message.channel
            and m.author.id == str(user)
            and any(is_link(word) for word in m.content.split(' '))
        )

        await self.bot.delete_message(last_m)

        silenced_message = ' '.join(
            f'<{word}>' if is_link(word) else word
            for word in last_m.content.split(' ')
        )

        await self.send_message(
            message.channel,
            f'<@{user}> said: {silenced_message}'
        )

    @command(p.string('!attention') + p.bind(p.mention, 'user'), global_cooldown(180, True))
    async def attention(self, message, user):
        user = self.bot.find_user(str(user))
        self.debug(user.avatar_url)
        avatar_url = user.avatar_url[user.avatar_url.index('avatars/')+len('avatars/'):user.avatar_url.rindex('.')]
        await self.send_message(
            message.channel,
            'https://ilovetotalkaboutmyself.com/#{}'.format(avatar_url)
        )

    # @command(p.string('!rydgel'))
    # async def rydgel(self, message):
    #     # saved
    #     await self.send_message(message.channel, 'test globibot')

    # @command(
    #     p.string('!zetaha') + p.bind(p.int_range(0, 10), 'i')
    #                         + p.bind(p.mention,          'user')
    #                         + p.bind(p.maybe(p.word),    'opt_word'),
    #     global_cooldown(10)
    # )
    # async def some_retarded_cmd(self, message, i, user, opt_word=None):
    #     await self.send_message(
    #         message.channel,
    #         f'i = {i}, user={user}, opt_word={opt_word}'
    #     )

    @command(p.string('!interject'), global_cooldown(30, True))
    async def interject(self, message):
        await self.send_message(
            message.channel,
            "I'd just like to __interject__ for a moment. What you're referring to as Linux, is in fact, **GNU/Linux**, or as I've recently taken to calling it, **GNU plus Linux**."
        )

    @command(p.string('!general'), global_cooldown(120, True))
    async def general(self, message):
        await self.send_message(
            message.channel,
            GENERAL_DESCRIPTION
        )

    @command(p.string('!gophers'), global_cooldown(30, True))
    async def gophers(self, message):
        await self.send_message(
            message.channel,
            ' '.join('*{}*'.format(name) for name, _ in self.gophers)
        )

    @command(p.string('!gopher') + p.bind(p.maybe(p.word), 'match'), global_cooldown(30, True))
    async def gopher(self, message, match=None):
        gopher_files = [f for _, f in self.gophers]
        if match:
            filtered_gopher_files = [
                f for name, f in self.gophers
                if match.lower() in name.lower()
            ]
            if filtered_gopher_files:
                gopher_files = filtered_gopher_files
            else:
                await self.send_message(
                    message.channel,
                    'I don\'t have any gopher for `{}`'.format(match)
                )
        gopher_file = '{}'.format(choice(gopher_files))

        await self.send_file(
            message.channel,
            gopher_file
        )

    @command(p.string('!toxic?'), global_cooldown(120, True))
    async def toxic_test(self, message):
        text = message.clean_content[8:]
        url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=AIzaSyDUQwNRONRAgf7NsSt70jv0PPL_X0WOXsA'
        keys = (
            'attack_on_author', 'attack_on_commenter', 'incoherent', 'inflammatory',
            'likely_to_reject', 'obscene', 'severe_toxicity', 'spam',
            'toxicity', 'unsubstantial',
        )
        body = {
            'comment': { 'text': text },
            'languages': ["en"],
            'requestedAttributes': {
                key.upper(): { }
                for key in keys
            },
        }

        tornado_future = self.http_client.fetch(
            url,
            body=json.dumps(body),
            method='POST',
            headers={ 'Content-Type': 'application/json' }
        )
        future = to_asyncio_future(tornado_future)
        response = await future

        data = json_decode(response.body.decode('utf8'))
        self.debug(data)

        text = ' '.join(
            f"{key}: `{data['attributeScores'][key.upper()]['summaryScore']['value'] * 100:.2f}%`"
            for key in keys
        )
        await self.send_message(
            message.channel,
            text
        )

    @command(p.string('!wiki'), global_cooldown(45))
    async def wiki(self, message):
        query = message.clean_content.strip()[len('!wiki'):].strip()

        params = urlencode((
            ('action', 'query'),
            ('list', 'search'),
            ('srsearch', query),
            ('format', 'json'),
            ('utf8', '')
        ))
        url = 'https://en.wikipedia.org/w/api.php?{}'.format(params)

        try:
            tornado_future = self.http_client.fetch(url)
            future = to_asyncio_future(tornado_future)
            response = await future

            data = json_decode(response.body.decode('utf8'))
            results = data['query']['search']
        except:
            await self.send_message(
                message.channel,
                'The Wikipedia API errored'
            )
        else:
            if not results:
                await self.send_message(
                    message.channel,
                    'No results for __{}__'.format(query)
                )
            else:
                top, *rest = results

                wiki_link = lambda title: 'https://en.wikipedia.org/wiki/{}'.format(quote(title))
                top_result = wiki_link(top['title'])

                await self.send_message(
                    message.channel,
                    top_result,
                )

                if rest:
                    matches = '\n'.join(
                        '[{}]({})'.format(match['title'], wiki_link(match['title']))
                        for match in rest
                    )
                    embed = Embed(
                        description='More results for __{}__:\n{}'.format(query, matches)
                    )

                    await self.send_message(
                        message.channel,
                        '',
                        embed=embed
                    )

    @command(p.string('!bg'), global_cooldown(60, True))
    async def bg(self, message):
        await self.send_message(
            message.channel,
            "https://cdn.discordapp.com/attachments/84822922958487552/395952882966331393/shorty.png"
        )

    # @command(p.string('!autism'), global_cooldown(60, True))
    # async def autism(self, message):
    #     await self.send_message(
    #         message.channel,
    #         "https://cdn.discordapp.com/attachments/84822922958487552/318883703466098699/unknown.png"
    #     )

    @command(p.string('!unblock'), master_only)
    async def unblock_all(self, message):
        await self.send_message(
            message.channel,
            '@everyone is unblocked'
        )

    @command(p.string('!new') + p.bind(p.mention, 'who'), global_cooldown(30, True))
    async def new(self, message, who):
        await self.send_message(
            message.channel,
            (
                '{}, if you want authentic real time 1on1 action with lirik, you need to donate 1000 bits every 30 minutes and make sure you complain about how mods remove your attention banner above chat to appeal to Lirik\'s emotional side.\n\n'
                'Also, never forget to spam chat before and after stream. Saying "hi" to literally every name in chat gives you a lot of lines too which in turn makes your penis ENORMOUS!\n\n'
                'Good luck on your path on becoming a mod, hope to still see ya here after 5 months when you realize that\'s not gonna happen 🙂'
            ).format(f.mention(who))
        )

    @command(p.string('!marc'), global_cooldown(90, True))
    async def marc(self, message):
        e = Embed(
            title="Daddy Marc 👶",
            description="IT'S A GIRL!"
        )
        e.set_thumbnail(url='https://cdn.discordapp.com/avatars/95160792428580864/a_50458d37b37b6f9fc04460c8fff708c0.webp')
        e.set_image(url='https://cdn.discordapp.com/attachments/84822922958487552/398507989058977812/IMG-20180104-WA0005.jpeg')
        e.set_footer(text=':3')

        m = await self.send_message(
            message.channel,
            content='',
            embed=e
        )
        await self.bot.add_reaction(m, '👧')

    @command(p.string('!faze'))
    async def faze(self, message):
        await self.bot.send_file(
            message.channel,
            '/tmp/globibot/faze.png'
        )

    @command(p.string('!vp'), user_cooldown(30, True))
    async def vp(self, message):
        await self.bot.send_file(
            message.channel,
            '/tmp/globibot/VP.png'
        )

    @command(p.string('!c9'))
    async def c9(self, message):
        await self.bot.send_file(
            message.channel,
            '/tmp/globibot/c9.png'
        )

    @command(p.string('!tts'), master_only)
    async def tts(self, message):
        try:
            await self.bot.delete_message(message)
        except:
            pass
        await self.send_message(
            message.channel,
            message.content.strip()[5:],
            tts=True
        )

    # @command(p.string('!elvi'), global_cooldown(90, True))
    # async def elvi(self, message):
    #     await self.send_message(
    #         message.channel,
    #         # 'https://cdn.discordapp.com/attachments/161251611405058048/447879798216458240/IMG_20180520_234050.jpg'
    #         'https://cdn.discordapp.com/attachments/161251611405058048/461921755879964682/IMG_20180628_150007.jpg'
    #     )

    @command(p.string('!mimsy'), global_cooldown(30, True))
    async def mimsy(self, message):
        await self.send_message(
            message.channel,
            'https://cdn.discordapp.com/attachments/178321904904568832/383591932384903170/unknown.png'
            # 'https://cdn.discordapp.com/attachments/384019485881008128/412932524231229440/image.jpg'
        )

    @command(p.string('!ichi'), global_cooldown(30, True))
    async def ichi(self, message):
        await self.send_message(
            message.channel,
            'https://imgur.com/FbV6c0b'
        )

    @command(p.string('!diehard'), global_cooldown(30, True))
    async def diehard(self, message):
        await self.send_message(
            message.channel,
            "**I am a diehard lirik fan. I go around to other chatrooms to make sure people know; That i am infact a lirik sub. Every 5 minutes I send a single <:lirikNbot:318917235412303872> and see if people respond. IT is my duty. I must connect with other lirik subs around twitch and be sure to let the streamer know that I ONLY sub to lirik. <:lirikNbot:318917235412303872> . Also, NO ONE RPs like lirik does. He's the funniest. He's the greatest. All other streamers need to know how shit they are.**"
        )

    @command(p.string('!pizza') + p.bind(p.mention, 'user_id'), global_cooldown(60, True))
    async def pizza(self, message, user_id):
        await self.send_message(
            message.channel,
            f'{f.mention(user_id)} idk how you do it, but you get the least appetizing pizza i\'ve ever seen\n'
            'I just don\'t get it. like the crust and stuff looks fine. but like.. the toppings. It\'s not so fucking hard to place more pepperoni on that.\n'
            'not only that it\'s just thrown about all willy nilly like. like oh this slice gets 1 pepperoni. "But it\'s artisan certified italian pizza" yeah so is digiornos'
        )

    # @command(p.string('!scan') + p.string('autism'))
    # async def autism_scan(self, message):
    #     if message.author.id not in AUTISM_SCAN_ALLOWED_USERS:
    #         return

    #     m = await self.send_file(
    #         message.channel,
    #         '/tmp/globibot/scan-autism.gif',
    #         content='Scanning current autism levels. Please wait...'
    #     )

    #     await asyncio.sleep(7)
    #     await self.bot.delete_message(m)

    #     frame_number = randint(0, 6)
    #     frame_path = '/tmp/globibot/scan-autism-{}.png'.format(frame_number)

    #     await self.send_file(
    #         message.channel,
    #         frame_path,
    #         content='Autism level scanning complete',
    #         delete_after=30
    #     )

    # A bit too harsh maybe

    # @command(p.string('!blocked') + p.bind(p.mention, 'user'), global_cooldown(90, True))
    # async def blocked(self, message, user):
    #     await self.send_message(
    #         message.channel,
    #         "{mention} I blocked you because you're the dumbest fucking ice tard I've seen in here next to impala.\n"
    #         "You are so dumb, I don't want your messages popping up on my screen on the off chance I accidentally read it.\n"
    #         "You're a waste of space. I'd rather have a fucking cat sit on a keyboard spamming nonsensical messages into the discord than read your shit.\n"
    #         "You're worthless in my eyes and a burden to this community. You constantly spread lies and misinformation.\n"
    #         "I whole heartedly mean this {mention} and I say this from the bottom of my heart.\n"
    #         "I actually think you have a disability. And I really wish that your mother swallowed you."
    #             .format(mention=f.mention(user))
    #     )

    @command(p.string('!galaxy'), global_cooldown(60, True))
    async def galaxy(self, message):
        await self.send_message(
            message.channel,
            'https://cdn.discordapp.com/attachments/84822922958487552/327858823702511627/Discord_2017-06-23_18-06-08.png'
        )

    @command(p.string('!isis'), global_cooldown(60, True))
    async def isis(self, message):
        await self.send_message(
            message.channel,
            'https://imgur.com/8UJRX92'
        )

    @command(p.string('!dutch'), global_cooldown(30, True))
    async def dutch(self, message):
        await self.send_message(
            message.channel,
            'http://imgur.com/rfsZSoF'
        )

    @command(p.string('!jj'), global_cooldown(60, True))
    async def jj(self, message):
        await self.send_message(
            message.channel,
            'https://i.imgur.com/LBB9oXG.png https://i.imgur.com/Scs4uXM.png'
        )

    @command(p.string('!patent'), global_cooldown(60, True))
    async def patent(self, message):
        await self.send_message(
            message.channel,
            'Here is CC attempting to draw the word __**patent**__: https://cdn.discordapp.com/attachments/84822922958487552/328641924703715348/unknown.png'
        )

    @command(p.string('!binoculars'), global_cooldown(60, True))
    async def binoculars(self, message):
        await self.send_message(
            message.channel,
            'Here is Fafa attempting to draw __**binoculars**__: https://i.imgur.com/VBNTz8k.jpg'
        )

    @command(p.string('!toolbox'), global_cooldown(60, True))
    async def toolbox(self, message):
        await self.send_message(
            message.channel,
            'Fafa\'s toolbox: https://i.imgur.com/XrfItRz.jpg'
        )

    @command(p.string('!jason'), global_cooldown(60, True))
    async def jason(self, message):
        await self.send_message(
            message.channel,
            'https://cdn.discordapp.com/attachments/84822922958487552/457832073865068545/unknown.png'
        )

    @command(p.string('!vix'), global_cooldown(60, True))
    async def vic(self, message):
        await self.send_message(
            message.channel,
            'https://i.imgur.com/4xJZenN.png'
        )

    @command(p.string('!dopamine'), global_cooldown(60, True))
    async def dopamine(self, message):
        now = datetime.datetime.now()
        weekday = calendar.day_name[now.weekday()]
        hour = now.time().strftime("%-I%p")
        await self.send_message(
            message.channel,
            f'wow! thousands of people sitting inside typing in discord on a {weekday} at {hour} LMAO. bout to hit the pool with some dime piece i matched on tinder and her friends to play beerpong and club. she wants me so bad it\'s not even funny haha. not gonna smash til i get something to eat though because sex kills gains. have fun watching the stream i guess lol.. later idiots'
        )

    @command(p.string('!marcus'), global_cooldown(60, True))
    async def marcus(self, message):
        await self.send_message(
            message.channel,
            "I want women to literally start touching me out of admiration and i wanna start MMA, like I wanna hit people. I feel like my ego so small compared to my body cause I've never been in physical conflict with people. i always talk myself out of fights. I'm pretty sure if i get to kick and punch people on the daily, my personality will improve and i will be truly the same as how I feel, better than everyone else. Last week 4 months i have focused on talking less about other people and i already see the results. people hit me up on whatsapp and ask me out etc. My motivation comes from my desire to see how much better I am than those filthy peasants"
        )

    @command(p.string('!loser') + p.bind(p.mention, 'user_id'), global_cooldown(60, True))
    async def loser(self, message, user_id):
        await self.send_message(
            message.channel,
            f"So you go by {f.mention(user_id)} now loser. Yeah that's right it's me Marcus. Sorry I used to give you a hard time in discord you were just an easy target. I drive a drop top Porsche and make over 300k a year. Can't believe you still play these stupid videogames. Nice catching up loser lol"
        )

    # @command(p.string('!sylf'), global_cooldown(60, True))
    # async def sylf(self, message):
    #     self.complaints += 1
    #     await self.send_message(
    #         message.channel,
    #         f'<@85477486925721600>\'s complained {self.complaints} times'
    #     )
    #     with open('/tmp/globibot/complaints', 'w') as f:
    #         f.write(f'{self.complaints}')

    @command(p.string('!drge'), global_cooldown(60, True))
    async def drge(self, message):
        await self.send_message(
            message.channel,
            'https://cdn.discordapp.com/attachments/84822922958487552/478146208943177728/Knipsel.PNG'
        )

    @command(p.string('!jeff'), global_cooldown(60, True))
    async def jeff(self, message):
        await self.send_message(
            message.channel,
            'https://cdn.discordapp.com/attachments/84822922958487552/478168244033814529/Screenshot_20180812-124800_01.png'
        )

    async def add_animal(self, message, key, galore):
        new_urls = [attachment['proxy_url'] for attachment in message.attachments]

        with open(f'/tmp/globibot/animals_galore/{galore.file_name}', 'r+') as f:
            urls = json.load(f) + new_urls
            f.seek(0)
            f.write(json.dumps(list(set(urls))))
            f.truncate()
            shuffle(urls)
            self.animal_galore[key] = AnimalGalore(
                galore.pet_owner_id,
                galore.file_name,
                cycle(urls)
            )

        await self.bot.add_reaction(message, '✅')

    async def on_reaction_add(self, reaction, user):
        if user.id == self.bot.user.id:
            return

        if reaction.emoji == '➕':
            if reaction.message.author == user:
                key, galore = next(
                    (k, g) for k, g in self.animal_galore.items()
                    if g.pet_owner_id == reaction.message.author.id
                )
                await self.bot.clear_reactions(reaction.message)
                await self.add_animal(reaction.message, key, galore)

        if reaction.emoji == '🇹' or reaction.emoji == '🇨':
            if reaction.message.author.id == '107400135952093184':
                if reaction.message.author == user:
                    key = 'ciri' if reaction.emoji == '🇨' else 'triss'
                    galore = self.animal_galore[key]
                    await self.bot.clear_reactions(reaction.message)
                    await self.add_animal(reaction.message, key, galore)

        if reaction.emoji == '🇦' or reaction.emoji == '🇹' or reaction.emoji == '🇱':
            if reaction.message.author.id == '449607034917093379':
                if reaction.message.author == user:
                    key = {
                        '🇦': 'alphacas',
                        '🇹': 'trico',
                        '🇱': 'leon',
                    }[reaction.emoji]
                    galore = self.animal_galore[key]
                    await self.bot.clear_reactions(reaction.message)
                    await self.add_animal(reaction.message, key, galore)

        if reaction.emoji == '🇳' or reaction.emoji == '🇵':
            if reaction.message.author.id == '157555104197771264':
                if reaction.message.author == user:
                    key = 'nola' if reaction.emoji == '🇳' else 'peach'
                    galore = self.animal_galore[key]
                    await self.bot.clear_reactions(reaction.message)
                    await self.add_animal(reaction.message, key, galore)

        if reaction.emoji == self.hide_link_emoji:
            if reaction.count >= 5:
                await self.bot.delete_message(reaction.message)

                silenced_message = ' '.join(
                    f'<{word}>' if is_link(word) else word
                    for word in reaction.message.content.split(' ')
                )

                await self.send_message(
                    reaction.message.channel,
                    f'I suppressed the previews of {reaction.message.author.mention}\'s message: {silenced_message}'
                )

    async def on_reaction_remove(self, reaction, user):
        if user.id == self.bot.user.id:
            return

    async def on_member_join(self, member):
        pass

    @command(p.string('!dashadow'))
    async def dashadow(self, message):
        await self.send_message(message.channel, 'Hey everyone, <@86236797582987264> here, please give me some attention')

    async def check_message_lang(self, message):
        text = re.sub(RE_EMOJI, '', message.content)
        text = re.sub(RE_MENTION, '', text)

        if len(text) < 15 or len(text.split(' ')) < 3:
            return

        query = urlencode({ 'q': text })
        url = f'https://ws.detectlanguage.com/0.2/detect?{query}'

        tornado_future = self.http_client.fetch(
            url,
            headers={ 'Authorization': 'Bearer 0428c255d6eac48312591e24ac8c9b53' }
        )
        future = to_asyncio_future(tornado_future)
        response = await future

        data = json_decode(response.body.decode('utf8'))
        detection = data['data']['detections'][0]

        if detection['isReliable']:
            lang = detection['language'].lower()
            if lang != 'en':
                try:
                    flag = FLAGS_PER_LANG[lang]
                except KeyError:
                    flag = ''.join(REGIONAL_INDICATORS[l] for l in lang)
                await self.bot.add_reaction(message, flag)

    @command(p.string('!factorio'))
    async def factorio_restart(self, message):
        ALLOWED_FACTORIO_USERS = (
            '98469035703832576',
            '81253500993937408',
            '89108411861467136'
        )
        if message.author.id not in ALLOWED_FACTORIO_USERS:
            return

        args = [
            arg for arg in message.clean_content[9:].strip().split(' ')
            if arg
        ]

        await self.send_message(
            message.channel,
            f'running command: `factorio {" ".join(args)}`...'
        )

        url = url_concat('http://172.17.0.1:8899/factorio', dict(args=' '.join(args)))

        tornado_future = self.http_client.fetch(url)
        future = to_asyncio_future(tornado_future)
        response = await future

        await self.send_message(
            message.channel,
            response.body.decode('utf8')
        )

    # @command(p.string('!frowns') + p.eof)
    # async def frowns(self, message):
    #     await self.send_message(message.channel, ' '.join(self.frown_faces))

    # @command(
    #     p.string('!frowns') + p.string('add') + p.bind(p.word, 'frown'),
    #     master_only
    # )
    # async def add_frown(self, message, frown):
    #     self.frown_faces.append(frown)
    #     with open('/tmp/globibot/frowns', 'w') as f:
    #         json.dump(self.frown_faces, f)
    #     m = await self.send_message(
    #         message.channel,
    #         'Recomputing frown count...'
    #     )
    #     self.frown_count, message_count = self.compute_frown_count()
    #     await self.send_message(
    #         message.channel,
    #         'Found {} frowns in {} messages'.format(
    #             self.frown_count, message_count
    #         )
    #     )
    #     await self.bot.delete_message(m)

    def compute_frown_count(self):
        with self.transaction() as trans:
            ilike = ' or '.join(
                'content ilike \'%%{}%%\''.format(frown_face)
                for frown_face in self.frown_faces
            )
            q = '''
                select content from log
                    where ({})
                    and author_id = %(user_id)s
                    and server_id = %(server_id)s
            '''.format(ilike)
            trans.execute(q, dict(
                user_id = 392581936662446080,
                server_id = 84822922958487552,
            ))
            messages = trans.fetchall()
            return sum(
                sum(m[0].count(face) for face in self.frown_faces)
                for m in messages
            ), len(messages)

    @command(p.string('!twitch-player'), global_cooldown(60, True))
    async def tp(self, message):
        await self.send_message(
            message.channel,
            'https://glo.bi/twitch-player_win32_online.exe'
        )

    @command(p.string('!peachN'), global_cooldown(90, True))
    async def peachn(self, message):
        await self.send_message(
            message.channel,
            "https://imgur.com/gSc50Yo"
        )

    @command(p.string('!pet') + p.string('random'), global_cooldown(90, True))
    async def random_pet(self, message):
        owner = choice(list(self.animal_galore.keys()))
        await self.send_message(
            message.channel,
            next(self.animal_galore[owner].urls)
        )

    @command(p.string('!peach'), global_cooldown(90, True))
    async def peach(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['peach'].urls)
        )

    @command(p.string('!nola'), global_cooldown(90, True))
    async def nola(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['nola'].urls)
        )

    @command(p.string('!gingerbois'), global_cooldown(90, True))
    async def gingerbois(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['becca'].urls)
        )

    @command(p.string('!minxy'), global_cooldown(90, True))
    async def minxy(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['minxy'].urls)
        )

    @command(p.string('!alpaca') | p.string('!alphaca'), global_cooldown(90, True))
    async def alphaca(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['alphacas'].urls)
        )

    @command(p.string('!baldcat'), global_cooldown(90, True))
    async def baldcat(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['loki'].urls)
        )

    @command(p.string('!pickles'), global_cooldown(90, True))
    async def pickles(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['pickles'].urls)
        )

    @command(p.string('!ciri'), global_cooldown(90, True))
    async def ciri(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['ciri'].urls)
        )

    @command(p.string('!triss'), global_cooldown(90, True))
    async def triss(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['triss'].urls)
        )

    @command(p.string('!maja'), global_cooldown(90, True))
    async def wito(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['wito'].urls)
        )

    @command(p.string('!trico'), global_cooldown(90, True))
    async def trico(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['trico'].urls)
        )

    @command(p.string('!leon'), global_cooldown(90, True))
    async def leon(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['leon'].urls)
        )

    @command(p.string('!pawson'), global_cooldown(90, True))
    async def pawson(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['pawson'].urls)
        )

    @command(p.string('!harvey'), global_cooldown(90, True))
    async def harvey(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['harvey'].urls)
        )

    @command(p.string('!ezio'), global_cooldown(90, True))
    async def ezio(self, message):
        await self.send_message(
            message.channel,
            next(self.animal_galore['ezio'].urls)
        )

    # @command(p.string('!e') + p.bind(p.integer, 'n'), global_cooldown(180, True))
    # async def e3(self, message, n):
    #     if (n != 3):
    #         return
    #     await self.send_message(
    #         message.channel,
    #         'Schedule: https://i.imgur.com/eiabfHL.png\nCountdown: <http://www.e3countdown.com/>\nRecap: <https://2018.e3recap.com/>'
    #     )

    @command(p.string('!reno'), global_cooldown(60, True))
    async def reno(self, message):
        await self.send_message(
            message.channel,
            'https://cdn.discordapp.com/attachments/178321904904568832/443184290251931658/unknown.png'
        )

    # @command(p.string('!sylfuss'), global_cooldown(60, True))
    # async def sylfuss(self, message):
    #     await self.send_message(
    #         message.channel,
    #         'https://cdn.discordapp.com/attachments/84822922958487552/441557782638886935/rGpGguW.png'
    #     )

    @command(p.string('!walzy'), global_cooldown(60, True))
    async def walzy(self, message):
        await self.send_message(
            message.channel,
            'https://cdn.discordapp.com/attachments/84822922958487552/507933088337362954/20181102_150402.jpg'
        )

    @command(p.string('!steppy'), global_cooldown(60, True))
    async def steppy(self, message):
        await self.send_message(
            message.channel,
            'https://cdn.discordapp.com/attachments/84822922958487552/513136574762844160/image0.png'
        )

    @command(p.string('!dab-on') + p.bind(p.mention, 'user') + p.bind(p.on_off_switch, 'on'), master_only)
    async def dabon(self, message, user, on):
        if on:
            self.dab_ons.add(str(user))
            self.debug(self.dab_ons)
        else:
            try:
                self.dab_ons.remove(str(user))
            except KeyError:
                pass

    async def on_delete(self, message):
        if message.channel.id != LIRIK_GENERAL:
            return

    async def on_new(self, message):
        # Animal galore owner reaction
        if message.channel.id == '105119939995643904':
            has_attachments = len(message.attachments) > 0
            pet_owners = (g.pet_owner_id for g in self.animal_galore.values())
            if has_attachments and message.author.id in pet_owners:
                if message.author.id == '107400135952093184': # para 2 cats
                    await self.bot.add_reaction(message, '🇨')
                    await self.bot.add_reaction(message, '🇹')
                elif message.author.id == '449607034917093379': # fellan 3 animals
                    await self.bot.add_reaction(message, '🇦')
                    await self.bot.add_reaction(message, '🇹')
                    await self.bot.add_reaction(message, '🇱')
                elif message.author.id == '157555104197771264': # Emma 2 animals
                    await self.bot.add_reaction(message, '🇵')
                    await self.bot.add_reaction(message, '🇳')
                else:
                    await self.bot.add_reaction(message, '➕')

        if message.channel.id == LIRIK_GENERAL:
            if message.author.id in self.dab_ons:
                dab_emoji = next(self.dab_emojis)
                await self.bot.add_reaction(message, dab_emoji)

        # if message.channel.id == LIRIK_GENERAL:
        #     if message.author.id == '181487392404799488':
        #         if self.wheelchair_counter == 0:
        #             await self.bot.add_reaction(message, '♿')
        #             self.wheelchair_counter += 1
        #             self.wheelchair_counter %= 15

        if message.channel.id == '462629869474283521':
            if message.author.id not in self.wc_speakers:
                await self.bot.delete_message(message)
                await self.send_message(
                    message.author,
                    "Hello, this is a friendly reminder that the channel you posted a message on is a channel for people who are watching the match through: http://glo.bi/wc2018/\n"
                    "If you are watching the game elsewhere, you probably have less delay than the people in there and **you should not be posting spoilers**\n"
                    "I deleted your message in case it was a spoiler. You can now speak in this chatroom if you are willing to follow the rules"
                )
                self.wc_speakers.add(message.author.id)

        # if message.em

        # if message.channel.id == LIRIK_GENERAL and message.author.id == '89108411861467136':
        #     if '😊' not in message.clean_content:
        #         await self.send_message(message.channel, '😊')

        # pepo_names = ('pepohmm', 'monkahmm', 'pepehmm', 'pepohm')
        # if message.channel.id == LIRIK_GENERAL:
        #     if any(f'<:{name}:' in message.content.lower() for name in pepo_names):
        #         now = time()
        #         if now - self.last_pepo < 60:
        #             await self.bot.delete_message(message)
        #             await self.send_message(
        #                 message.channel,
        #                 f'hmm avalable in {60 - (now - self.last_pepo):.2f} seconds',
        #                 delete_after = 5
        #             )
        #         else:
        #             self.last_pepo = now

        if message.channel.id == LIRIK_GENERAL and message.author.id == '392581936662446080':
            used_faces = [
                face for face in self.frown_faces
                if face in message.clean_content
            ]
            if used_faces:
                for face in used_faces:
                    self.frown_count += message.clean_content.count(face)
                await self.send_message(
                    message.channel,
                    'frown count: {}'.format(self.frown_count)
                )

        if '*runs away*' in message.clean_content:
            await self.send_file(
                message.channel,
                '/tmp/globibot/runsaway.gif',
                delete_after = 45
            )

        if '*here we go*' in message.clean_content:
            await self.send_file(
                message.channel,
                '/tmp/globibot/herewego.gif',
                delete_after = 45
            )

        if message.author.id == '98589509347704832':
            words = message.clean_content.split(' ')
            for word in words:
                if len(word) == 4 and word.upper() == word:
                    await self.send_message(self.channel, 'https://jackbox.tv#{}'.format(word))
                    break

        if message.channel.id == LIRIK_GENERAL:
            await self.add_toxicity_sample(message)

        if message.channel.id == LIRIK_GENERAL or message.channel.id == '178321904904568832':
        # if message.channel.id == '178321904904568832':
            await self.check_message_lang(message)

        # if message.channel.id == LIRIK_GENERAL:
        #     words = message.clean_content.split(' ')
        #     if any(is_link(word) for word in words):
        #         await self.bot.add_reaction(message, self.hide_link_emoji)

        # if message.channel.id == LIRIK_GENERAL and message.author.id == '104713622340534272':
        #     if len(message.attachments) or 'http://' in message.clean_content or 'https://' in message.clean_content:
        #         await self.bot.add_reaction(message, '👍')
        #         await self.bot.add_reaction(message, '👎')

    @command(p.string('!wc'), global_cooldown(60, True))
    async def wc(self, message):
        content = (
            'Stream 1: http://glo.bi/wc2018/\n'
            'Rankings MPG: https://predict.mpg.football/rank/league/KDWYA7Y\n'
            'Rankings Sven: http://glo.bi/wc2018/rankings.html'
        )

        await self.send_message(message.channel, content)

    @command(p.string('!say'), master_only)
    async def say(self, message):
        try:
            await self.bot.delete_message(message)
        except:
            pass
        await self.send_message(
            message.channel,
            message.content[4:].strip()
        )

    @command(p.string('!drree'), global_cooldown(30, True), master_only)
    async def drree(self, message):
        await self.send_message(
            message.channel,
            '𝕏𝕚𝕚𝕒𝕞 𝕟𝕠𝕠𝕟𝕖 𝕚𝕟 𝕥𝕙𝕖𝕚𝕣 𝕣𝕚𝕘𝕙𝕥 𝕞𝕚𝕟𝕕 𝕨𝕠𝕦𝕝𝕕 𝕥𝕖𝕝𝕝 𝕥𝕙𝕖 𝕥𝕣𝕦𝕥𝕙 𝕨𝕙𝕖𝕟 𝕥𝕙𝕖𝕪 𝕔𝕒𝕟 𝕘𝕖𝕥 𝕒𝕨𝕒𝕪 𝕨𝕚𝕥𝕙 𝕒 𝕝𝕚𝕖. 𝕟𝕠𝕥 𝕠𝕟𝕝𝕪 𝕥𝕠 𝕡𝕣𝕠𝕥𝕖𝕔𝕥 𝕡𝕖𝕣𝕤𝕠𝕟𝕒𝕝 𝕚𝕟𝕗𝕠𝕣𝕞𝕒𝕥𝕚𝕠𝕟 𝕓𝕦𝕥 𝕒𝕝𝕤𝕠 𝕥𝕠 𝕡𝕣𝕠𝕥𝕖𝕔𝕥 𝕥𝕙𝕖𝕞𝕤𝕖𝕝𝕧𝕤 𝕗𝕣𝕠𝕞 𝕡𝕖𝕠𝕡𝕝𝕖. 𝕌 𝕨𝕚𝕝𝕝 𝕟𝕖𝕧𝕖𝕣 𝕜𝕟𝕠𝕨 𝕞𝕖 𝕠𝕣 𝕨𝕙𝕒𝕥 𝕚 𝕒𝕞, 𝕨𝕙𝕪 𝕥𝕙𝕖 𝕗𝕦𝕔𝕜 𝕨𝕠𝕦𝕝𝕕 𝕚 𝕤𝕙𝕠𝕨 𝕦 𝕠𝕣 𝕥𝕖𝕝𝕝 𝕪𝕠𝕦 ?'
        )

    @command(p.string('!disco'), global_cooldown(30, True))
    async def disco(self, message):
        await self.send_message(
            message.channel,
            'ＷＨＡＴ ＩＳ ＴＨＥＲＥ ＮＯＴ ＴＯ ＬＩＫＥ ＡＢＯＵＴ ＤＩＳＣＯ? ＳＨＥ ＩＳ ＡＣＴＵＡＬＬＹ ＲＥＡＬＬＹ ＳＭＡＲＴ, ＲＥＡＬＬＹ ＮＩＣＥ, ＮＯＴ ＤＲＩＶＥＮ ＢＹ ＤＲＡＭＡ. １０/１０ ＳＨＯＲＴＹ ＳＨＯＵＬＤ ＭＡＲＲＹ ＨＥＲ.'
        )

    @command(p.string('!fluffeh'), global_cooldown(60, True))
    async def fluffeh(self, message):
        await self.send_message(
            message.channel,
            '😃 🛡 🗡 https://pre00.deviantart.net/ed03/th/pre/i/2015/353/d/0/guard_by_wlop-d9kmnxu.jpg'
        )

    # @command(p.string('!jeff'), global_cooldown(60, True))
    # async def jeff(self, message):
    #     await self.send_message(
    #         message.channel,
    #        'https://cdn.discordapp.com/attachments/331590195088457728/386167156120748053/tKd5Ua6.png'
    #     )

    @command(p.string('!ocr'), global_cooldown(60, True))
    async def ocr(self, message):
        if not message.attachments:
            return

        url = message.attachments[0]['url']

        tornado_future = self.http_client.fetch(url)
        future = to_asyncio_future(tornado_future)
        response = await future

        _, path = tempfile.mkstemp('.png')
        with open(path, 'wb') as fi:
            fi.write(response.body)

        m = await self.send_message(message.channel, 'Processing...')
        await self.bot.edit_message(
            m,
            f.code_block(pytesseract.image_to_string(Image.open(path)))
        )

    # @command(p.string('!bitcoin'), global_cooldown(60 * 5, True))
    # async def bitcoin(self, message):
    #     await self.send_message(
    #         message.channel,
    #         'What the fuck did you just fucking say about bitcoin, you little bitch? I’ll have you know I used to mine bitcoins, and I’ve been using them since 2010, I once bought a pizza for 10k bitcoins, and now have over 2 confirmed bitcoins. I am trained in cryptocurrency and I’m the top sniper in the entire US markets. You are nothing to me but just another wannabe investor. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying random buzzwords you heard over the Internet? Think again, fucker. As we speak I am contacting my secret network of miners across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your investment portfolio. You’re fucking dead, kid. I can be anywhere, anytime, and I can steal your investments in over seven hundred ways, and that’s just with my bare hands. Not only am I extensively trained in back hacking crypto wallets, but I have access to the entire arsenal of the Wall Street and I will use it to its full extent to wipe your miserable investments off the face of the continent, you little shit. If only you could have known what unholy retribution your little “clever” comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will shit fury all over your cryptocurrency knowledge and you will drown in it. You’re fucking dead, kiddo.'
    #     )

    @command(p.string('!ghostfr'), global_cooldown(60, True))
    async def ghostfr(self, message):
        await self.send_message(
            message.channel,
            'https://gfycat.com/OldfashionedIdleBeauceron'
        )

    @command(p.string('!purgebot'))
    async def purgeme(self, message):
        try:
            await self.bot.delete_message(message)
        except:
            pass

        async for log in self.bot.logs_from(message.channel, limit=100):
            if log.author == self.bot.user:
                await self.bot.delete_message(log)

    @command(
        p.string('!rateme'),
        global_cooldown(15, True)
    )
    async def rateme(self, message):
        try:
            rate = RATE_FIXED[message.author.id]
        except KeyError:
            rate = randint(1, 9)

        reaction = RATE_REACTIONS[rate]
        await self.send_message(
            message.channel,
            '{} you are an __HB{}__ {}'.format(message.author.mention, rate, reaction)
        )

    @command(
            p.string('!timeto')
        +   p.oneplus(p.some_type(p.TokenType.Space))
        +   p.bind(p.many(p.any_type >> p.to_s), 'raw_topic'),
        global_cooldown(30, True),
        ignored_tokens = (),
    )
    async def timeto(self, message, raw_topic):
        topic = ''.join(raw_topic)

        content = f'''
What time is it?
                 12
      11     ⭡      1
  10        │          2
9           ⊙—⮞     3  Time to
   8                    4        {topic}
       7           5
             6
'''

        await self.send_message(message.channel, content)

    @command(p.string('!w'), global_cooldown(60, True))
    async def weather(self, message):
        city = message.clean_content[3:].strip()
        query = urlencode({ 'q': 'weather {}'.format(city) })
        await self.send_message(
            message.channel,
            '{} here you go: http://lmgtfy.com/?{}'.format(message.author.mention, query)
        )

    async def maffs_fight(self, message, user1, user2):
        plus = lambda a, b: a + b
        minus = lambda a, b: a - b
        times = lambda a, b: a * b

        ops_str = { plus: '+', minus: '-', times: 'x' }

        ops = (plus, minus, times)
        r = [n for n in range(-50, -20)] + [p for p in range(20, 50)]
        a, b, op = choice(r), choice(r), choice(ops)
        result = op(a, b)
        eq_str = '{} {} {}'.format(a, ops_str[op], b if b >= 0 else '({})'.format(b))

        # a = randint(0, 64)
        # result = a
        # eq_str = 'the decimal form of {}'.format(bin(a))
        await self.send_message(
            message.channel,
            "First one to give the result of `{}` wins"
                .format(eq_str)
        )

        message_from_u1 = self.bot.wait_for_message(author=self.bot.find_user(str(user1)), channel=message.channel)
        message_from_u2 = self.bot.wait_for_message(author=self.bot.find_user(str(user2)), channel=message.channel)

        done, _ = await asyncio.wait((message_from_u1, message_from_u2), return_when=asyncio.FIRST_COMPLETED)

        first_answer = done.pop().result()
        winner, loser = user1, user2
        m = ""
        if first_answer.clean_content.strip() == str(result):
            m = "correct: `{} = {}`".format(eq_str, result)
            if first_answer.author.id == str(user2):
                winner, loser = user2, user1
        else:
            m = "incorrect: `{} = {} and not '{}'`".format(eq_str, result, first_answer.clean_content.strip())
            if first_answer.author.id == str(user1):
                winner, loser = user2, user1

        cause = 'with superior math skills'
        await self.send_message(
            message.channel,
            '{}\n{} killed {} {}'.format(m, f.mention(winner), f.mention(loser), cause)
        )

    async def redirect_to_trivia(self, message, user1, user2):
        await self.send_message(
            message.channel,
            'please use !trivia <subject> instead'
        )

    async def random_fight(self, message, user1, user2):
        # rigged_users = [
        #     '89108411861467136', # globi
        #     '98469035703832576', # sven
        #     '245948225872199680', # derk
        # ]

        # rigged = False
        # for rigged_user in rigged_users:
        #     if rigged_user == str(user1):
        #         winner, loser = user1, user2
        #         rigged = True
        #         break
        #     elif rigged_user == str(user2):
        #         winner, loser = user2, user1
        #         rigged = True
        #         break

        # if not rigged:
        winner = choice((user1, user2))
        loser = user1 if winner == user2 else user2

        while True:
            cause = choice(FIGHT_TEXTS)
            if cause not in self.last_fights:
                self.last_fights.insert(0, cause)
                self.last_fights = self.last_fights[:20]
                break

        await self.send_message(
            message.channel,
            '{} killed {} {}'.format(f.mention(winner), f.mention(loser), cause)
        )

    # @command(p.string('!flag') + p.bind(p.word, 'country'), user_cooldown(30, True))
    # async def flag(self, message, country):
    #     try:
    #         image = next(img for ctry, img in self.flags if ctry.lower() == country.lower())
    #     except StopIteration:
    #         await self.send_message(
    #             message.channel,
    #             '{} I did not find any flag for `{}`'.format(message.author.mention, country)
    #         )
    #     else:
    #         await self.send_message(
    #             message.channel,
    #             'https://www.countries-ofthe-world.com/{}'.format(image)
    #         )

    @command(
        p.string('!fight') + p.bind(p.mention, 'user1') +
                             p.bind(p.mention, 'user2') +
                             p.maybe(p.bind(p.word, 'fight_type')),
        global_cooldown(5, True)
    )
    async def fight(self, message, user1, user2, fight_type=None):
        if user1 == user2:
            return

        if str(user1) == self.bot.user.id or str(user2) == self.bot.user.id:
            await self.send_message(
                message.channel,
                '{} I win. I always win <:EZ:373119673014812673>'
                    .format(message.author.mention)
            )
            return

        try:
            fight_logic = self.fights[fight_type]
        except KeyError:
            fight_logic = self.random_fight

        await fight_logic(message, user1, user2)

    async def on_member_update(self, before, after):
        if after.id == LIRIK_ID:
            if not after.game or after.game.type == 1:
                return

            if after.game != self.last_game:
                self.last_game = after.game
                message = 'Lirik is now playing `{}`'.format(after.game.name)

                await self.send_message(self.channel, message)

    @command(p.string('!css'))
    async def css(self, message):
        await self.send_message(
            message.channel,
            '__**EXTRACT**__ that archive and follow the instructions: {}\n'
            'Video demo: {}'
                .format(
                    'https://glo.bi/discord-globi-css.zip',
                    'https://streamable.com/4rdy6'
                )
        )

    @command(p.string('!sleepover') + p.bind(p.maybe(p.mention), 'user'), global_cooldown(15, True))
    async def sleepover(self, message, user=None):
        pj = choice(PJS)
        user = user if user else message.author.id
        await self.send_message(
            message.channel,
            '<@{}> welcome to the sleepover, grab a pj and come cuddle 😊\n{}'.format(user, pj)
        )

    @command(p.string('!poll'), master_only)
    async def poll(self, message):
        poll_data = message.clean_content[5:].strip()
        title, *options = poll_data.split('\n')

        if not options:
            return

        emotes = list(POLL_EMOTES)
        shuffle(emotes)

        embed = Embed(
            title=title,
            description='\n'.join(
                f'{emotes[i]} - __**{option}**__'
                for i, option in enumerate(options)
            )
        )

        m = await self.send_message(
            message.channel,
            '',
            embed=embed
        )

        for i in range(len(options)):
            await self.bot.add_reaction(m, emotes[i])
