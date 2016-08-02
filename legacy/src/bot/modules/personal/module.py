from bot.lib.module import Module
from bot.lib.decorators import command
from bot.lib.helpers import parsing as p

from .command import ImagesCommand, GoogleCommand, YoutubeCommand
from .errors import PrefixNotSubstring, NoUrlsGiven

from . import constants as c

from time import time

class Personal(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.commands = dict()

        self.google_api_key = self.config.get(c.GOOGLE_API_KEY_KEY)
        self.google_search_engine_cx = self.config.get(c.GOOGLE_SEARCH_ENGINE_CX_KEY)

    async def on_message(self, message):
        try:
            command = self.commands[message.author.id]
            if message.content.startswith('!{}'.format(command.prefix)):
                await command.call(self, message)
        except KeyError:
            pass

    async def register_command(self, message, prefix, command_cls, *args):
        try:
            old_command = self.commands[message.author.id]
            if time() - old_command.created_at < c.CHANGE_COOLDOWN:
                return
        except KeyError:
            pass

        prefix = prefix.lower()

        if prefix not in message.author.name.lower():
            raise PrefixNotSubstring

        command = command_cls(prefix)
        await command.initialize(*args)
        self.commands[message.author.id] = command

        await self.send_message(
            message.channel,
            '{}, your personnal command: `!{}` has been registered'
                .format(message.author.mention, prefix)
        )

    prefix = p.string('!my')
    set_prefix = prefix + p.string('set')

    @command(
        set_prefix + p.bind(p.word, 'prefix') +
        p.string('images') + p.bind(p.many(p.url), 'urls')
    )
    async def register_urls_command(self, message, prefix, urls):
        if not urls:
            raise NoUrlsGiven

        await self.register_command(
            message,
            prefix,
            ImagesCommand, urls
        )

    @command(
        set_prefix + p.bind(p.word, 'prefix') +
        p.string('google') + p.bind(p.many(p.some_type(p.TokenType.Word)), 'theme')
    )
    async def register_google_command(self, message, prefix, theme):
        if not theme:
            return

        theme = ' '.join(theme)
        await self.register_command(
            message,
            prefix,
            GoogleCommand, theme,
            self.google_api_key, self.google_search_engine_cx
        )

    @command(
        set_prefix + p.bind(p.word, 'prefix') +
        p.string('youtube') + p.bind(p.many(p.some_type(p.TokenType.Word)), 'theme')
    )
    async def register_youtube_command(self, message, prefix, theme):
        if not theme:
            return

        theme = ' '.join(theme)
        await self.register_command(
            message,
            prefix,
            YoutubeCommand, theme, self.google_api_key
        )
