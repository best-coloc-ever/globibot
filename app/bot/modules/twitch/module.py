from ..base import Module, command, master_only

from .emote_store import EmoteStore
from .kappa import Kappa

from collections import defaultdict

class Twitch(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.emote_disabled_channels = set()
        self.emote_store = EmoteStore()
        self.emote_sizes = defaultdict(lambda: EmoteStore.LARGE)

        self.kappa = Kappa(self.emote_store, self.send_message, self.send_file)
        self.kappa_mode = False

        self.info('loaded {} twitch emotes'.format(
            len(self.emote_store.url_store))
        )

    @command('!emote Kappa on', master_only)
    async def enable_kappa_mode(self, message):
        self.kappa_mode = True

        await self.send_message(
            message.channel,
            'Kappa mode is `enabled` for emotes'
        )

    @command('!emote Kappa off', master_only)
    async def disable_kappa_mode(self, message):
        self.kappa_mode = False

        await self.send_message(
            message.channel,
            'Kappa mode is `disabled` for emotes'
        )

    @command('!emote Kappa level {level:f}')
    async def set_kappa_level(self, message, level):
        if level >= 0. and level <= 1.0:
            self.kappa.level = level

            await self.send_message(
                message.channel,
                'Kappa mode is at `{}` %'.format(level * 100)
            )

    @command('!emote enable', master_only)
    async def enable_emotes(self, message):
        self.debug(
            'Enabling emotes in {}#{}'.format(message.server, message.channel)
        )

        self.emote_disabled_channels.discard(message.channel)

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

        self.emote_disabled_channels.add(message.channel)

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

        if channel not in self.emote_disabled_channels:
            size = self.emote_sizes[channel]
            if self.kappa_mode:
                await self.kappa.reply_to_emote(message, emote_name, size)
            else:
                emote_file = self.emote_store.get(emote_name, size)
                if emote_file:
                    await self.send_file(channel, emote_file)

    @command('!emote reload', master_only)
    async def reload_emotes(self, message):
        self.emote_store = EmoteStore()
        self.kappa.emote_store = self.emote_store

        await self.send_message(
            message.channel,
            'loaded {} twitch emotes'.format(
                len(self.emote_store.url_store)
            )
        )
