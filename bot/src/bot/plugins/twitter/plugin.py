from bot.lib.plugin import Plugin
from bot.lib.decorators import command

from bot.lib.helpers import parsing as p
from bot.lib.helpers import formatting as f
from bot.lib.helpers.hooks import master_only

from . import constants as c
from . import queries as q
from . import errors as e

from twitter import Twitter as TwitterAPI
from twitter import OAuth

from collections import namedtuple
from time import strptime

import asyncio

MonitoredChannel = namedtuple(
    'MonitoredChannel',
    ['id', 'user_id', 'server_id']
)

def format_tweet(tweet):
    text = (
        'Last tweet from `@{screen_name}`:\n\n'
        '{text}\n'
        '**{retweets}** 🔄   **{favourites}** 👍'
    ).format(
        screen_name = tweet['user']['screen_name'],
        text        = f.code_block(tweet['text']),
        retweets    = tweet['retweet_count'],
        favourites  = tweet['favorite_count']
    )

    try:
        entities = tweet['extended_entities']['media']
        media_urls = [entity['media_url_https'] for entity in entities]
        text += (
            '\n\nMedia files attached in the tweet:\n{}'
                .format('\n'.join(media_urls))
        )
    except:
        pass

    return text

tweet_time = lambda tweet: strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')

class Twitter(Plugin):

    def load(self):
        self.oauth = OAuth(
            self.config.get(c.ACCESS_TOKEN_KEY),
            self.config.get(c.ACCESS_TOKEN_SECRET_KEY),
            self.config.get(c.CONSUMER_KEY_KEY),
            self.config.get(c.CONSUMER_SECRET_KEY),
        )

        self.client = TwitterAPI(auth=self.oauth)

        self.monitored = set()
        self.restore_monitored()

    def unload(self):
        self.monitored.clear()

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
        tweets = self.get_tweets(user['id'], count=1)

        if tweets:
            tweet = tweets[0]
            m = await self.send_message(
                message.channel,
                format_tweet(tweet),
                delete_after=60
            )
            self.run_async(self.update_tweet(tweet, m))

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

            self.run_async(self.monitor_forever(user_id, message.server))

            await self.send_message(
                message.channel,
                'Now monitoring `{}` tweets'.format(screen_name),
                delete_after=15
            )

    @command(
        twitter_prefix + p.string('unmonitor') + p.bind(p.word, 'screen_name'),
        master_only
    )
    async def unmonitor(self, message, screen_name):
        user = self.get_user(screen_name=screen_name)
        user_id = user['id']

        if user_id not in self.monitored:
            return

        del self.monitored[user_id]

        with self.transaction() as trans:
            trans.execute(q.remove_monitored, dict(
                user_id   = user_id,
                server_id = message.server.id
            ))

        await self.send_message(
            message.channel,
            'Stopped monitoring `{}`'.format(screen_name),
            delete_after=15
        )

    @command(twitter_prefix + p.string('monitored'), master_only)
    async def monitored(self, message):
        with self.transaction() as trans:
            trans.execute(q.get_monitored)
            monitored = [MonitoredChannel(*row) for row in trans.fetchall()]

            users = [
                self.get_user_by_id(channel.user_id)['screen_name']
                for channel in monitored
                if str(channel.server_id) == message.server.id
            ]

            await self.send_message(
                message.channel,
                'I\'m currently monitoring the following channels:\n{}'
                    .format(f.code_block(users))
            )

    '''
    Details
    '''

    def get_user(self, screen_name):
        try:
            return self.client.users.lookup(screen_name=screen_name)[0]
        except Exception:
            raise e.UserNotFound(screen_name)

    def get_user_by_id(self, user_id):
        return self.client.users.lookup(user_id=user_id)[0]

    def get_tweets(self, user_id, count):
        try:
            return self.client.statuses.user_timeline(
                user_id=user_id,
                count=count,
                exclude_replies=True
            )
        except:
            return None

    def restore_monitored(self):
        with self.transaction() as trans:
            trans.execute(q.get_monitored)
            monitored = [MonitoredChannel(*row) for row in trans.fetchall()]

            for channel in monitored:
                server = next(
                    serv for serv in self.bot.servers
                    if serv.id == str(channel.server_id)
                )
                self.run_async(self.monitor_forever(channel.user_id, server))

    async def monitor_forever(self, user_id, server):
        self.monitored.add(user_id)

        tweets = self.get_tweets(user_id, count=1)
        if not tweets:
            return
        last_tweet = tweets[0]

        self.debug('Monitoring new tweets from {}'.format(user_id))

        while user_id in self.monitored:
            await asyncio.sleep(45)

            tweets = self.get_tweets(user_id, count=1)
            if tweets:
                latest = tweets[0]
                if latest['id'] != last_tweet['id']:
                    if tweet_time(latest) > tweet_time(last_tweet):
                        last_tweet = latest
                        m = await self.send_message(
                            server.default_channel,
                            format_tweet(latest)
                        )
                        self.run_async(self.update_tweet(latest, m))

        self.debug('No longer monitoring {}'.format(user_id))

    async def update_tweet(self, tweet, message):
        for i in range(6):
            await asyncio.sleep(5)
            try:
                tweet = self.client.statuses.show(id=tweet['id'])
                await self.edit_message(message, format_tweet(tweet))
            except Exception as e:
                self.error(e)
                pass
