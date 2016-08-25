from bot.lib.plugin import Plugin
from bot.lib.decorators import command

from bot.lib.helpers import parsing as p
from bot.lib.helpers import formatting as f
from bot.lib.helpers.hooks import master_only

from . import queries as q
from . import constants as c
from .api import TwitchAPI
from .pubsub import PubSub

from collections import namedtuple

import asyncio

MonitoredChannel = namedtuple(
    'MonitoredChannel',
    ['id', 'name', 'server_id']
)

class Twitch(Plugin):

    def load(self):
        self.client_id = self.config.get(c.CLIENT_ID_KEY)

        if not self.client_id:
            self.warning('Missing client id: API calls might not work')

        self.api = TwitchAPI(self.client_id, self.debug)
        self.pubsub = PubSub(self.debug, self.run_async)

        self.restore_monitored()

    def unload(self):
        asyncio.ensure_future(self.pubsub.shutdown())

    '''
    Commands
    '''

    twitch_prefix = p.string('!twitch')

    @command(twitch_prefix + p.string('status') + p.bind(p.word, 'name'))
    async def twitch_channel_status(self, message, name):
        stream, channel = await asyncio.gather(
            self.api.stream(name),
            self.api.channel(name)
        )

        response = '`{name}` is __{status}__'
        info = dict(
            name   = channel.display_name,
            status = 'online' if stream else 'offline'
        )

        if stream:
            response += ': `{title}`\n\n🕹 {game}\n👀 {viewers:,}\n'
            online_info = dict(
                title   = stream.channel.status,
                game    = stream.game,
                viewers = stream.viewers
            )

            info = {**info, **online_info}

        await self.send_message(
            message.channel,
            response.format(**info),
            delete_after=15
        )

    twitch_top_prefix = twitch_prefix + p.string('top')

    @command(twitch_top_prefix + p.string('games')
                               + p.bind(p.maybe(p.integer), 'count'))
    async def twitch_top_games(self, message, count=10):
        top_games = await self.api.top_games(count)

        info = [
            (top_game.game.name,
            '📺 {:,}'.format(top_game.channels),
            '👀 {:,}'.format(top_game.viewers))
            for top_game in top_games
        ]

        await self.send_message(
            message.channel,
            'Top {} games on Twitch right now\n{}'
                .format(len(top_games), f.code_block(f.pad_rows(info, ' | '))),
            delete_after=15
        )

    @command(twitch_top_prefix + p.string('channels')
                               + p.bind(p.maybe(p.integer), 'count'))
    async def twitch_top_channels(self, message, count=10):
        streams = await self.api.top_channels(count)

        info = [
            (stream.channel.display_name,
            '🕹 {}'.format(stream.game),
            '👀 {:,}'.format(stream.viewers),
            stream.channel.status)
            for stream in streams
        ]

        await self.send_message(
            message.channel,
            'Top {} games on Twitch right now\n{}'
                .format(len(streams), f.code_block(f.pad_rows(info, ' | '))),
            delete_after=15
        )

    @command(
        twitch_prefix + p.string('monitor') + p.bind(p.word, 'name'),
        master_only
    )
    async def twitch_monitor(self, message, name):
        channel = await self.api.channel(name)

        with self.transaction() as trans:
            trans.execute(q.add_monitored, dict(
                name      = channel.name,
                server_id = message.server.id
            ))

            self.run_async(self.monitor_forever(channel.name, message.server))

            await self.send_message(
                message.channel,
                'Now monitoring `{}`'.format(channel.display_name),
                delete_after=15
            )

    @command(
        twitch_prefix + p.string('unmonitor') + p.bind(p.word, 'name'),
        master_only
    )
    async def twitch_unmonitor(self, message, name):
        channel = await self.api.channel(name)

        await self.pubsub.unsubscribe(
            PubSub.Topics.VIDEO_PLAYBACK(channel.name),
            message.server.id
        )

        with self.transaction() as trans:
            trans.execute(q.remove_monitored, dict(
                name      = channel.name,
                server_id = message.server.id
            ))

            await self.send_message(
                message.channel,
                'Stopped monitoring `{}`'.format(channel.display_name),
                delete_after=15
            )

    @command(twitch_prefix + p.string('monitored'), master_only)
    async def monitored(self, message):
        with self.transaction() as trans:
            trans.execute(q.get_monitored)
            monitored = [MonitoredChannel(*row) for row in trans.fetchall()]

            channels = [
                channel.name for channel in monitored
                if str(channel.server_id) == message.server.id
            ]

            await self.send_message(
                message.channel,
                'I\'m currently monitoring the following channels:\n{}'
                    .format(f.code_block(channels)),
                delete_after=15
            )

    '''
    Details
    '''

    async def monitor_forever(self, name, server):
        self.info('Monitoring: {}'.format(name))

        channel = await self.api.channel(name)
        events = await self.pubsub.subscribe(
            PubSub.Topics.VIDEO_PLAYBACK(channel.name),
            server.id
        )

        async for event in events:
            self.debug(event)
            if event['type'] == 'stream-up':
                await self.send_message(
                    server.default_channel,
                    '`{}` just went live!\n{}'
                        .format(channel.display_name, channel.url)
                )
            if event['type'] == 'stream-down':
                await self.send_message(
                    server.default_channel,
                    '`{}` just went offline 😢'.format(channel.display_name)
                )

        self.info('Stopped monitoring: {}'.format(name))

    def restore_monitored(self):
        with self.transaction() as trans:
            trans.execute(q.get_monitored)
            monitored = [MonitoredChannel(*row) for row in trans.fetchall()]

            for channel in monitored:
                server = next(
                    serv for serv in self.bot.servers
                    if serv.id == str(channel.server_id)
                )
                self.run_async(self.monitor_forever(channel.name, server))
