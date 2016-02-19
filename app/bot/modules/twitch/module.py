from ..base import Module, command, master_only

from .emote_store import EmoteStore

from collections import defaultdict

class Twitch(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.emote_enabled_channels = set()
        self.emote_store = EmoteStore()
        self.emote_sizes = defaultdict(lambda: EmoteStore.MEDIUM)

        self.info('loaded {} twitch emotes'.format(
            len(self.emote_store.url_store))
        )

    @command('!emote enable', master_only)
    async def enable_emotes(self, message):
        self.debug(
            'Enabling emotes in {}#{}'.format(message.server, message.channel)
        )

        self.emote_enabled_channels.add(message.channel)

        await self.send_message(
            message.channel,
            (
                '`Twitch emotes` are now **enabled** in this channel\n'
                'size is set to `{}`'
            ).format(self.emote_sizes[message.channel])
        )

    @command('!emote disable', master_only)
    async def disable_emotes(self, message):
        self.debug(
            'Disabling emotes in {}#{}'.format(message.server, message.channel)
        )

        self.emote_enabled_channels.discard(message.channel)

        await self.send_message(
            message.channel,
            '`Twitch emotes` are now **disabled** in this channel'
        )

    @command('!emote size {size:w}', master_only)
    async def change_emote_size(self, message, size):
        channel = message.channel
        size = size.lower()

        if not size in EmoteStore.SIZES:
            await self.send_message(
                channel,
                '`{}` is not a valid size'.format(size)
            )
        else:
            self.emote_sizes[channel] = size
            await self.send_message(
                channel,
                'Emotes are now `{}`'.format(size)
            )

    @command('!{emote_name:S}')
    @command('!<:{emote_name:S}:{:d}>')
    async def display_emote(self, message, emote_name):
        channel = message.channel

        if channel in self.emote_enabled_channels:
            size = self.emote_sizes[channel]
            emote_file = self.emote_store.get(emote_name, size)
            if emote_file:
                await self.send_file(channel, emote_file)

    @command('!emote reload', master_only)
    async def reload_emotes(self, message):
        self.emote_store = EmoteStore()

        await self.send_message(
            message.channel,
            'loaded {} twitch emotes'.format(
                len(self.emote_store.url_store)
            )
        )
