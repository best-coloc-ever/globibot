from bot.lib.plugin import Plugin
from bot.lib.decorators import command

from bot.lib.helpers import parsing as p
from bot.lib.helpers.hooks import master_only

from cleverbot import Cleverbot

class ChatBot(Plugin):

    def load(self):
        self.chat_bot = Cleverbot()

    @command(
        p.bind(p.mention, 'user') + p.bind(p.many(p.any_type), 'words'),
        master_only
    )
    async def answer(self, message, user, words):
        if str(user) != self.bot.user.id:
            return

        await self.bot.send_typing(message.channel)
        response = self.chat_bot.ask(message.content)

        if response:
            await self.send_message(
                message.channel,
                response
            )
