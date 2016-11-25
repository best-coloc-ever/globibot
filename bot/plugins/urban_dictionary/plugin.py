from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers.hooks import global_cooldown

from tornado.escape import json_decode
from tornado.httputil import url_concat
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.platform.asyncio import to_asyncio_future

from random import randint

from discord import Embed

def definition_embed(definition):
    embed = Embed(
        title       = 'Definition',
        description = definition['definition']
    )

    embed.set_author(
        name     = definition['word'],
        icon_url = 'http://www.urbandictionary.com/favicon.ico',
        url      = definition['permalink']
    )

    embed.add_field(
        name  = 'Example',
        value = '{}\n\n👍 {:,} 👎 {:,}'.format(
            definition['example'],
            definition['thumbs_up'],
            definition['thumbs_down'],
        )
    )

    embed.color = randint(0, 0xffffff)

    return embed

class UrbanDictionary(Plugin):

    def load(self):
        self.api_key = self.config.get('mashape_key')

        self.client = AsyncHTTPClient()

    @command(p.string('!define') + p.bind(p.word, 'term'), global_cooldown(30))
    async def define_word_command(self, message, term):
        definitions = await self.fetch_definitions(term)

        if definitions:
            by_thumbs_up = lambda d: d['thumbs_up']
            best_definition = sorted(definitions, key=by_thumbs_up)[-1]

            await self.send_message(
                message.channel, '',
                embed        = definition_embed(best_definition),
                delete_after = 60
            )

    DEFINE_URL = 'https://mashape-community-urban-dictionary.p.mashape.com/define'
    async def fetch_definitions(self, term):
        url = url_concat(UrbanDictionary.DEFINE_URL, dict(term=term))
        request = HTTPRequest(
            url     = url,
            headers = {
                'X-Mashape-Key': self.api_key,
                'Accept'       : 'text/plain'
            }
        )
        tornado_future = self.client.fetch(request)
        future = to_asyncio_future(tornado_future)
        response = await future

        data = json_decode(response.body)

        return data['list']
