from bot.lib.module import Module
from bot.lib.decorators import simple_command
from bot.lib.helpers.hooks import master_only

from . import constants as c

from twitter import Twitter as TwitterAPI
from twitter import TwitterStream
from twitter import OAuth

from collections import defaultdict

import asyncio

class Twitter(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.oauth = OAuth(
            self.config.get(c.ACCESS_TOKEN_KEY),
            self.config.get(c.ACCESS_TOKEN_SECRET_KEY),
            self.config.get(c.CONSUMER_KEY_KEY),
            self.config.get(c.CONSUMER_SECRET_KEY),
        )
        self.client = TwitterAPI(auth=self.oauth)

        self.users = {}
        self.streams = defaultdict(set)

    @simple_command('!tweet {name:w}')
    async def last_tweet(self, message, name):
        user = self.get_user(name)
        if user is None:
            await self.send_message(
                message.channel,
                'Unable to locate a user named `{}`'.format(name)
            )
        else:
            tweets = self.get_tweets(user, 1)
            if tweets is None:
                await self.send_message(
                    message.channel,
                    'Unable to fetch the timeline of `{}`'.format(name)
                )
            else:
                await self.send_message(
                    message.channel,
                    format_tweet(tweets[0])
                )

    @simple_command('!twitter monitor {name:w}', master_only)
    async def monitor_user(self, message, name):
        channel = message.channel

        if channel in self.streams[name]:
            await self.send_message(
                channel,
                'Already monitoring `{}`'.format(name)
            )
        else:
            user = self.get_user(name)
            if user is None:
                await self.send_message(
                    channel,
                    'Unable to locate a user named `{}`'.format(name)
                )
            else:
                self.streams[name].add(channel)
                asyncio.ensure_future(self.read_stream(name, user, channel))
                await self.send_message(
                    channel,
                    'Now monitoring `{}` tweets in this channel'.format(name)
                )

    @simple_command('!twitter unmonitor {name:w}', master_only)
    async def unmonitor_user(self, message, name):
        self.streams[name].discard(message.channel)

        await self.send_message(
            message.channel,
            'Stopped monitoring `{}` tweets in this channel'.format(name)
        )

    def get_user(self, name):
        try:
            return self.users[name]
        except KeyError:
            try:
                user = self.client.users.lookup(screen_name=name)[0]
                self.users[name] = user
                return user
            except:
                return None

    def get_tweets(self, user, count):
        try:
            return self.client.statuses.user_timeline(
                user_id=user['id'],
                count=count
            )
        except:
            return None

    async def read_stream(self, name, user, channel):
        stream =  TwitterStream(auth=self.oauth, timeout=0.1)
        iterator = stream.statuses.filter(follow=user['id'])

        for tweet in iterator:
            if channel not in self.streams[name]:
                break
            if tweet and 'text' in tweet:
                if tweet['user']['id'] == user['id']:
                    await self.send_message(
                        channel,
                        format_tweet(tweet)
                    )
            await asyncio.sleep(5)

def format_tweet(tweet):
    infos = {
        'screen_name': tweet['user']['screen_name'],
        'text': tweet['text'],
        'url': 'https://twitter.com/{}/status/{}'.format(
            tweet['user']['screen_name'],
            tweet['id']
        )
    }

    return (
        'Last tweet from `@{screen_name}`:\n'
        '```\n'
        '{text}\n'
        '```\n'
        'source: {url}'
    ).format(**infos)
