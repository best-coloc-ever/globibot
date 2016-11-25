from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import master_only

from . import queries as q
from . import constants as c
from .api import TwitchAPI
from .pubsub import PubSub
from .handlers import TwitchStatusHandler, OAuthRequestTokenHandler, \
    OAuthAuthorizeHandler, TwitchDisconnectHandler, TwitchFollowedHandler, \
    TwitchMentionHandler, TwitchWhisperHandler

from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.platform.asyncio import to_asyncio_future

from random import randint
from collections import namedtuple
from urllib.parse import urlencode

from discord import Embed

import random
import string
import asyncio

MonitoredChannel = namedtuple(
    'MonitoredChannel',
    ['id', 'name', 'server_id']
)

NotifiedChannel = namedtuple(
    'NotifiedChannel',
    ['name', 'method']
)

ChannelState = lambda name, state: dict(
    name = name,
    on = state
)

def twitch_alert_embed(channel, users):
    description = (
        '🕹 *{game}*\n'
        '👀 *{views:,}* '
        '❤ *{follows:,}*'
            .format(
                game    = channel.game,
                views   = channel.views,
                follows = channel.followers,
            )
    )

    embed = Embed(
        title       = 'Just went live!',
        description = description,
        url         = channel.url
    )

    embed.set_author(
        name     = channel.display_name,
        icon_url = 'https://twitch.tv/favicon.ico',
        url      = channel.url
    )

    if users:
        embed.add_field(
            name  = 'Wake up!',
            value = ' '.join(f.mention(user_id) for user_id in users)
        )

    embed.add_field(
        name  = 'Pro tip',
        value = 'You can now link your Twitch account on '
                '[globibot.com](https://globibot.com/#connections) '
                'to get notified when your favorite streamers go live',
    )

    embed.set_thumbnail(url=channel.logo)
    embed.color = randint(0, 0xffffff)

    return embed

class Twitch(Plugin):

    def load(self):
        self.client_id = self.config.get(c.CLIENT_ID_KEY)
        self.client_secret = self.config.get(c.CLIENT_SECRET_KEY)

        if not self.client_id:
            self.warning('Missing client id: API calls might not work')

        self.api = TwitchAPI(self.client_id, self.debug)
        self.pubsub = PubSub(self.debug, self.run_async)

        self.restore_monitored()

        context = dict(plugin=self, bot=self.bot)
        self.add_web_handlers(
            (r'/twitch/oauth', OAuthRequestTokenHandler, context),
            (r'/twitch/authorize', OAuthAuthorizeHandler, context),
            (r'/twitch/status', TwitchStatusHandler, context),
            (r'/twitch/followed', TwitchFollowedHandler, context),
            (r'/twitch/disconnect', TwitchDisconnectHandler, context),
            (r'/twitch/mention', TwitchMentionHandler, context),
            (r'/twitch/whisper', TwitchWhisperHandler, context),
        )

        self.token_states = dict()

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
            if event['type'] == 'stream-up':
                users = self.users_to_mention(name, server)
                await self.send_message(
                    server.default_channel, '',
                    embed = twitch_alert_embed(channel, users)
                )

            if event['type'] == 'stream-down':
                await self.send_message(
                    server.default_channel,
                    '`{}` just went offline 😢'.format(channel.display_name)
                )

        self.info('Stopped monitoring: {}'.format(name))

    async def whisper_monitor_forever(self, channel_name, user):
        events = await self.pubsub.subscribe(
            PubSub.Topics.VIDEO_PLAYBACK(channel_name),
            user.id
        )

        async for event in events:
            if event['type'] == 'stream-up':
                await self.send_message(
                    user,
                    '`{}` just went live!'
                        .format(channel_name)
                )

    def users_to_mention(self, channel_name, server):
        with self.transaction() as trans:
            trans.execute(q.get_subscribed_users, dict(
                channel = channel_name,
                method = 'mention'
            ))

            return [
                user_id for user_id, in trans.fetchall()
                if server in self.bot.servers_of(
                    self.bot.find_user(str(user_id))
                )
            ]

        return []

    def users_to_whisper(self, channel_name):
        with self.transaction() as trans:
            trans.execute(q.get_subscribed_users, dict(
                channel = channel_name,
                method = 'whisper'
            ))

            return [user_id for user_id, in trans.fetchall()]

        return []

    def restore_monitored(self):
        with self.transaction() as trans:
            # Server monitors
            trans.execute(q.get_monitored)
            monitored = [MonitoredChannel(*row) for row in trans.fetchall()]

            for channel in monitored:
                server = next(
                    serv for serv in self.bot.servers
                    if serv.id == str(channel.server_id)
                )
                self.run_async(self.monitor_forever(channel.name, server))

            # Whispers
            trans.execute(q.get_all_notify_whispers)

            for user_id, channel_name in trans.fetchall():
                user = self.bot.find_user(str(user_id))
                if user:
                    self.run_async(self.whisper_monitor_forever(channel_name, user))

    def request_token_state(self, user):
        state = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(32)
        )

        self.token_states[user.id] = state

        return state

    async def save_user(self, user, code, state):
        try:
            reference_state = self.token_states[user.id]
        except KeyError:
            return
        else:
            if state != reference_state:
                return

            token = await self.access_token(code, state)

            with self.transaction() as trans:
                trans.execute(q.add_user, dict(
                    id = user.id,
                    token = token
                ))

    TOKEN_URL = 'https://api.twitch.tv/kraken/oauth2/token'
    REDIRECT_URI = 'https://globibot.com/bot/twitch/authorize'
    async def access_token(self, code, state):
        client = AsyncHTTPClient()

        payload = (
            ('client_id', self.client_id),
            ('client_secret', self.client_secret),
            ('grant_type', 'authorization_code'),
            ('redirect_uri', Twitch.REDIRECT_URI),
            ('code', code),
            ('state', state),
        )

        url = Twitch.TOKEN_URL
        request = HTTPRequest(
            url = url,
            method = 'POST',
            body = urlencode(payload)
        )
        tornado_future = client.fetch(request)
        future = to_asyncio_future(tornado_future)
        response = await future

        data = json_decode(response.body)
        return data['access_token']

    def disconnect_user(self, user):
        with self.transaction() as trans:
            trans.execute(q.delete_user, dict(
                id = user.id
            ))

    def user_connected(self, user):
        with self.transaction() as trans:
            trans.execute(q.get_user, dict(id=user.id))

            if trans.fetchone():
                return True

        return False

    async def user_followed(self, user):
        token = self.get_user_token(user)

        followed = await self.api.user_followed(token)

        user_servers = self.bot.servers_of(user)
        with self.transaction() as trans:
            trans.execute(q.get_monitored_names, dict(
                server_ids = tuple(server.id for server in user_servers)
            ))

            monitored_names = set(name for name, in trans.fetchall())

            trans.execute(q.get_notified, dict(
                id = user.id,
            ))

            notifieds = [NotifiedChannel(*row) for row in trans.fetchall()]
            whipered = [
                notified.name for notified in notifieds
                if notified.method == 'whisper'
            ]
            mentionned = [
                notified.name for notified in notifieds
                if notified.method == 'mention'
            ]

            followed_channels = [ChannelState(f.channel.name, f.channel.name in whipered) for f in followed]
            monitored_channels = [ChannelState(name, name in mentionned) for name in monitored_names]

            return (
                followed_channels,
                monitored_channels
            )

        return ([], [])

    def get_user_token(self, user):
        with self.transaction() as trans:
            trans.execute(q.get_user, dict(id=user.id))

            return trans.fetchone()[0]

    def user_notify_mention(self, user, channel, state):
        payload = dict(
            id = user.id,
            channel = channel,
            method = 'mention'
        )

        query = q.user_notify_add if state else q.user_notify_remove

        with self.transaction() as trans:
            trans.execute(query, payload)

    async def user_notify_whisper(self, user, channel, state):
        payload = dict(
            id = user.id,
            channel = channel,
            method = 'whisper'
        )
        query = q.user_notify_add if state else q.user_notify_remove

        with self.transaction() as trans:
            trans.execute(query, payload)

            if state:
                self.run_async(self.whisper_monitor_forever(channel, user))
            else:
                await self.pubsub.unsubscribe(
                    PubSub.Topics.VIDEO_PLAYBACK(channel),
                    user.id
                )
