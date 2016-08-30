from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers.hooks import master_only

from cleverbot import Cleverbot

from collections import defaultdict

class ChatBot(Plugin):

    def load(self):
        self.chat_bot = Cleverbot()

        self.dm_bots = defaultdict(Cleverbot)

    @command(
        p.bind(p.mention, 'user') + p.bind((p.many(p.any_type >> p.to_s)), 'words'),
        master_only
    )
    async def answer(self, message, user, words):
        if str(user) != self.bot.user.id:
            return

        await self.bot.send_typing(message.channel)
        response = self.chat_bot.ask(' '.join(words))

        if response:
            await self.send_message(
                message.channel,
                response
            )

    @command(p.bind((p.many(p.any_type >> p.to_s)), 'words'))
    async def answer_dm(self, message, words):
        if message.server:
            return

        await self.bot.send_typing(message.channel)
        bot = self.dm_bots[message.author.id]
        response = bot.ask(' '.join(words))

        if response:
            await self.send_message(
                message.channel,
                response
            )
