from globibot.lib.plugin import Plugin

from globibot.lib.decorators import command  # Command declaration helper

from globibot.lib.helpers import parsing as p  # Parser combinator tools
from globibot.lib.helpers.hooks import master_only

from .handlers import VoiceHandler
from .ws_handler import VoiceWebSocketHandler
from .tts import TTSManager
from .player import ServerPlayer, ItemType, PlayerItem

from collections import defaultdict

from discord import Embed

import asyncio

user_data = lambda user: dict(
    id         = user.id,
    name       = user.name,
    avatar_url = user.avatar_url,
)

def item_data(item):
    data = dict(resource = item.resource, user=user_data(item.user))
    if item.type == ItemType.LocalFile:
        data['tts'] = True

    data.update(item.infos)

    return data

def required_skips_for(count):
    return int(1 + (count + 1) / 3)

class Dj(Plugin):

    def load(self):
        context = dict(plugin=self, bot=self.bot)
        self.add_web_handlers(
            (r'/voice', VoiceHandler, context),
            (r'/ws/voice', VoiceWebSocketHandler, context),
        )

        self.players = dict()
        self.volumes = defaultdict(lambda: 1.0)
        self.tts = TTSManager()

        self.ws_consumers = defaultdict(set)
        self.ongoing_skips = dict()

    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return

        if reaction.emoji == '🗳':
            await self.check_skips(reaction.message, reaction.count - 1)

    '''
    Commands
    '''

    @command(p.string('!tts'))
    async def say_command(self, message):
        content = message.clean_content[5:].strip()
        await self.queue_tts(message.server, message.author, content)

        await self.delete_message_after(message, 5)

    @command(p.string('!voteskip'))
    async def voteskip(self, message):
        if message.server.id in self.ongoing_skips:
            return

        player = self.get_player(message.server)

        embed = Embed(
            title       = 'Voteskip',
            description = 'Skip __{}__ ?'.format(player.items[0].resource)
        )
        embed.set_footer(text='Click the reaction below to cast your vote')

        m = await self.send_message(message.channel, '', embed=embed)
        await self.bot.add_reaction(m, '🗳')

        self.ongoing_skips[message.server.id] = m
        self.run_async(self.skip_timeout(message.server.id, m))

    @command(p.string('!tts-lang'))
    async def tts_lang_command(self, message):
        lang = message.clean_content[10:].strip()
        self.tts.set_server_language(message.server, lang)

        await self.delete_message_after(message, 5)

    @command(p.string('!play'))
    async def play(self, message):
        await self.queue_item(
            message.server,
            message.author,
            ItemType.YTDLLink,
            message.clean_content[6:].strip()
        )

        await self.delete_message_after(message, 5)

    @command(p.string('!skip'), master_only)
    async def skip(self, message):
        player = self.get_player(message.server)
        player.skip()

        await self.delete_message_after(message, 5)

    @command(p.string('!volume') + p.bind(p.integer, 'vol'), master_only)
    async def volume(self, message, vol):
        if vol < 0 or vol > 100:
            return

        vol = float(vol) / 100
        self.volumes[message.server.id] = vol
        player = self.get_player(message.server)
        player.player.volume = vol

    '''
    Helpers
    '''

    async def check_skips(self, message, count):
        try:
            skip_m = self.ongoing_skips[message.server.id]
        except KeyError:
            pass
        else:
            if skip_m.id == message.id:
                user_count = len(self.bot.voice_client_in(skip_m.server).channel.voice_members) - 1
                if count >= required_skips_for(user_count):
                    player = self.get_player(skip_m.server)
                    player.skip()

                    del self.ongoing_skips[message.server.id]
                    await self.bot.delete_message(message)

    async def skip_timeout(self, server_id, m):
        await asyncio.sleep(30)
        try:
            skip_m = self.ongoing_skips[server_id]
        except:
            pass
        else:
            if skip_m.id == m.id:
                await self.bot.delete_message(m)
                del self.ongoing_skips[server_id]

    async def queue_tts(self, server, user, content, lang=None):
        sound_file = self.tts.talk_in(server, content, lang)

        await self.queue_item(
            server,
            user,
            ItemType.LocalFile,
            sound_file
        )

    async def join_voice(self, channel):
        voice = self.bot.voice_client_in(channel.server)
        if voice is None:
            await self.bot.join_voice_channel(channel)
        else:
            await voice.move_to(channel)

    async def queue_item(self, server, user, type, resource):
        try:
            item = PlayerItem(type, resource, user)
        except Exception as e:
            self.notify_ws_error(server, str(e), resource)
        else:
            player = self.get_player(server)
            await player.enqueue(item)
            self.notify_ws_queue(server, item)

    def get_player(self, server):
        try:
            player = self.players[server.id]
        except KeyError:
            get_volume = lambda: self.volumes[server.id]
            player = ServerPlayer(server, self.bot.voice_client_in, get_volume)
            self.players[server.id] = player
            on_next = lambda item: self.notify_ws_next(server, item)
            self.run_async(player.start(self.error, on_next))

        return player

    def notify_ws_next(self, server, item):
        data = dict(type='next', playing=item_data(item))

        self.notify_ws(server, data)

    def server_queue_data(self, server):
        player = self.get_player(server)

        return dict(
            type      = 'queue_data',
            items     = [item_data(item) for item in player.items],
            server_id = server.id
        )

    def notify_ws_error(self, server, error, resource):
        data = dict(type='error', error=error, resource=resource)
        self.notify_ws(server, data)

    def notify_ws_queue(self, server, item):
        data = dict(type='queue', item=item_data(item))

        self.notify_ws(server, data)

    def notify_ws(self, server, data):
        data['server_id'] = server.id

        for consumer in self.ws_consumers[server.id]:
            consumer.write_message(data)

