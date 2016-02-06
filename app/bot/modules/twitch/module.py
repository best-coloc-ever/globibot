from ..base import Module, command

from .emote_store import EmoteStore

class Twitch(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.emote_enabled_channels = set()
        self.emote_store = EmoteStore()

    @command('!emote enable')
    async def enable_emotes(self, message):
        self.emote_enabled_channels.add(message.channel)

        message = '`Twitch emotes` are now **enabled** in this channel'
        await self.respond(message)

    @command('!emote disable')
    async def disable_emotes(self, message):
        self.emote_enabled_channels.discard(message.channel)

        message = '`Twitch emotes` are now **disabled** in this channel'
        await self.respond(message)

    @command('{emote_name:w}')
    async def display_emote(self, message, emote_name):
        if message.channel in self.emote_enabled_channels:
            emote_file = self.emote_store.get(emote_name)
            if emote_file:
                await self.respond_file(emote_file)
