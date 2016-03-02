from bot.lib.module import Module
from bot.lib.decorators import command
from bot.lib.helpers.hooks import master_only
from bot.lib.helpers import parsing as p

from .emote_store import EmoteStore
from .kappa import Kappa

from parse import parse

from collections import defaultdict

import random

class Twitch(Module):

    prefix = p.string('!emote')

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

    @command(prefix + p.bind(p.on_off_switch, 'enabled'), master_only)
    async def enable_emotes(self, message, enabled):
        if enabled:
            self.emote_disabled_channels.discard(message.channel)
        else:
            self.emote_disabled_channels.add(message.channel)

        await self.send_message(
            message.channel,
            '`Twitch emotes` are now **{}** in this channel\n'
                .format('enabled' if enabled else 'disabled')
        )

    kappa_prefix = prefix + p.string('Kappa')

    @command(kappa_prefix + p.bind(p.on_off_switch, 'enabled'), master_only)
    async def enable_kappa_mode(self, message, enabled):
        self.kappa_mode = enabled

        await self.send_message(
            message.channel,
            'Kappa mode is `{}` for emotes'
                .format('enabled' if enabled else 'disabled')
        )

    kappa_level = p.int_range(0, 100)
    @command(kappa_prefix + p.bind(kappa_level, 'level'), master_only)
    async def set_kappa_level(self, message, level):
        self.kappa.level = float(level) / 100

        await self.send_message(
            message.channel,
            'Kappa mode is at `{}` %'.format(level)
        )

    emote_size = p.one_of(p.string, *EmoteStore.SIZES) >> p.to_s
    @command(prefix + p.bind(emote_size, 'size'), master_only)
    async def change_emote_size(self, message, size):
        channel = message.channel
        size = size.lower()

        self.emote_sizes[channel] = size
        await self.send_message(
            channel,
            'Emotes are now `{}`'.format(size)
        )

    @command(prefix + p.string('reload'), master_only)
    async def reload_emotes(self, message):
        self.emote_store = EmoteStore()
        self.kappa.emote_store = self.emote_store

        await self.send_message(
            message.channel,
            'loaded {} twitch emotes'.format(
                len(self.emote_store.url_store)
            )
        )

    def find_emote(self, word):
        EMOTE_FORMAT = '<:{emote_name:S}:{:d}>'

        if word.startswith('!'):
            name = word[1:]
            if name in self.emote_store.url_store.keys():
                return name
            parsed = parse(EMOTE_FORMAT, name)
            if parsed:
                return parsed.named['emote_name']

    @command(p.bind(p.many(p.any_type), 'words'))
    async def emotes(self, message, words):
        emotes = [
            emote for emote in [self.find_emote(word) for word in words]
            if emote
        ]

        await self.display_emotes(message.channel, emotes)

    async def display_emotes(self, channel, emotes):
        if channel not in self.emote_disabled_channels and emotes:
            size = self.emote_sizes[channel]
            emote_file = self.emote_store.assemble(emotes, size)
            if emote_file:
                await self.send_file(channel, emote_file)

    @command(
        prefix + p.string('random') +
        p.bind(p.maybe(p.int_range(1, 10)), 'count')
    )
    async def random_emote(self, message, count=1):
        emote_names = list(self.emote_store.url_store.keys())
        random.shuffle(emote_names)

        await self.display_emotes(message.channel, emote_names[:count])
        await self.send_message(
            message.channel,
            '({})'.format(', '.join(emote_names[:count]))
        )

    @command(prefix + p.string('theme') + p.bind(p.word, 'theme'))
    async def themed(self, message, theme):
        emote_names = list(self.emote_store.url_store.keys())
        random.shuffle(emote_names)

        themed_emote_names = [
            emote_name for emote_name in emote_names
            if theme.lower() in emote_name.lower()
        ][:10]

        await self.display_emotes(message.channel, themed_emote_names)
        await self.send_message(
            message.channel,
            '({})'.format(', '.join(themed_emote_names))
        )
