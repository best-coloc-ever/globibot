from bot.lib.plugin import Plugin
from bot.lib.decorators import command

from bot.lib.helpers import parsing as p
from bot.lib.helpers import formatting as f
from bot.lib.helpers.hooks import master_only

from . import constants as c
from . import queries as q
from . import errors as e

from twitter import Twitter as TwitterAPI
from twitter import TwitterStream
from twitter import OAuth

from collections import namedtuple

import asyncio

MonitoredChannel = namedtuple(
    'MonitoredChannel',
    ['id', 'user_id', 'server_id']
)

def format_tweet(tweet):
    return (
        'Last tweet from `@{screen_name}`:\n\n'
        '{text}\n'
        '**{retweets}** 🔄   **{favourites}** 👍'
    ).format(
        screen_name = tweet['user']['screen_name'],
        text        = f.code_block(tweet['text']),
        retweets    = tweet['retweet_count'],
        favourites  = tweet['user']['favourites_count']
    )

class Twitter(Plugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.oauth = OAuth(
            self.config.get(c.ACCESS_TOKEN_KEY),
            self.config.get(c.ACCESS_TOKEN_SECRET_KEY),
            self.config.get(c.CONSUMER_KEY_KEY),
            self.config.get(c.CONSUMER_SECRET_KEY),
        )
        self.client = TwitterAPI(auth=self.oauth)

    '''
    Commands
    '''

    twitter_prefix = p.string('!twitter')

    @command(
        twitter_prefix + p.string('last') + p.bind(p.word, 'screen_name'),
        master_only
    )
    async def last_tweet(self, message, screen_name):
        user = self.get_user(screen_name=screen_name)
        tweets = self.get_tweets(user, count=1)

        if tweets:
            await self.send_message(
                message.channel,
                format_tweet(tweets[0]),
                delete_after=60
            )

    @command(
        twitter_prefix + p.string('monitor') + p.bind(p.word, 'screen_name'),
        master_only
    )
    async def monitor(self, message, screen_name):
        user = self.get_user(screen_name=screen_name)
        user_id = user['id']

        with self.transaction() as trans:
            trans.execute(q.add_monitored, dict(
                user_id   = user_id,
                server_id = message.server.id
            ))

            future = self.monitor_forever(user_id, message.server)
            asyncio.ensure_future(future)

            await self.send_message(
                message.channel,
                'Now monitoring `{}` tweets'.format(screen_name),
                delete_after=15
            )

    @command(twitter_prefix + p.string('monitored'), master_only)
    async def monitored(self, message):
        with self.transaction() as trans:
            trans.execute(q.get_monitored)
            monitored = [MonitoredChannel(*row) for row in trans.fetchall()]

            users = [
                self.get_user(user_id=channel.user_id)['screen_name']
                for channel in monitored
                if str(channel.server_id) == message.server.id
            ]

            await self.send_message(
                message.channel,
                'I\'m currently monitoring the following channels:\n{}'
                    .format(f.code_block(users))
            )

    @command(twitter_prefix + p.string('restore'), master_only)
    async def restore(self, message):
        with self.transaction() as trans:
            trans.execute(q.get_monitored)
            monitored = [MonitoredChannel(*row) for row in trans.fetchall()]

            for channel in monitored:
                server = next(
                    serv for serv in self.bot.servers
                    if serv.id == str(channel.server_id)
                )
                future = self.monitor_channel(channel.user_id, server)
                asyncio.ensure_future(future)

    '''
    Details
    '''

    def get_user(self, screen_name):
        try:
            return self.client.users.lookup(screen_name=screen_name)[0]
        except Exception:
            raise e.UserNotFound(screen_name)

    def get_tweets(self, user, count):
        try:
            return self.client.statuses.user_timeline(
                user_id=user['id'],
                count=count
            )
        except:
            return None

    async def monitor_channel(self, user_id, server):

        while True:
            self.info('Building stream iterator')
            stream = TwitterStream(auth=self.oauth, block=False)
            iterator = stream.statuses.filter(follow=user_id)

            for tweet in iterator:
                if tweet and 'text' in tweet:
                    self.debug(tweet)
                    if tweet['user']['id'] == user_id:
                        await self.send_message(
                            server.default_channel,
                            format_tweet(tweet)
                        )
                self.debug('{}: No new tweet'.format(user_id))
                await asyncio.sleep(15)

            self.info('Stream iterator hung up')
            await asyncio.sleep(15)

