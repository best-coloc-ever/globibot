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

def definition_embed(definitions, index):
    definition = definitions[index]

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

    embed.set_footer(text='definition {} / {}'.format(index + 1, len(definitions)))

    embed.color = randint(0, 0xffffff)

    return embed

class UrbanDictionary(Plugin):

    def load(self):
        self.api_key = self.config.get('mashape_key')

        self.client = AsyncHTTPClient()

        self.definitions_by_message = dict()

    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return

        show_prev = (reaction.emoji == '⬅')
        show_next = (reaction.emoji == '➡')

        if not show_prev and not show_next:
            return

        message = reaction.message

        try:
            (definitions, index) = self.definitions_by_message[message.id]
        except KeyError:
            pass
        else:
            new_index = index + 1 if show_next else index - 1

            if new_index < 0 or new_index >= len(definitions):
                return

            new_embed = definition_embed(definitions, new_index)

            await self.bot.clear_reactions(message)
            await self.bot.edit_message(message, '', embed=new_embed)

            self.definitions_by_message[message.id] = (definitions, new_index)

            if new_index > 0:
                await self.bot.add_reaction(message, '⬅')
            if new_index < (len(definitions) - 1):
                await self.bot.add_reaction(message, '➡')

    @command(p.string('!define') + p.bind(p.word, 'term'), global_cooldown(30))
    async def define_word_command(self, message, term):
        definitions = await self.fetch_definitions(term)

        if definitions:
            by_thumbs_up = lambda d: d['thumbs_up']
            sorted_definitions = sorted(definitions, key=by_thumbs_up, reverse=True)

            message = await self.send_message(
                message.channel, '',
                embed        = definition_embed(sorted_definitions, 0),
                delete_after = 120
            )

            await self.register_definition_message(message, sorted_definitions)

    async def register_definition_message(self, message, definitions):
        if len(definitions) >= 2:
            await self.bot.add_reaction(message, '➡')

            self.definitions_by_message[message.id] = (definitions, 0)

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
