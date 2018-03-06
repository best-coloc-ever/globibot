from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import master_only

from . import constants as c
from . import queries as q
from . import errors as e
from .handlers import OAuthTokenHandler, OAuthAuthorizeHandler, \
                      TwitterStatusHandler, TwitterDisconnectHandler

from .api import TwitterApi, Credentials as TwitterCredentials

from collections import namedtuple
from functools import partial
from datetime import datetime
from time import time as now

from discord import Embed

import asyncio
import re

import twitter
MonitoredChannel = namedtuple(
    'MonitoredChannel',
    ['id', 'user_id', 'server_id', 'channel_id']
)

OAuthUser = namedtuple(
    'OAuthUser',
    ['token', 'secret']
)

tweet_time = lambda tweet: datetime.strptime(
    tweet['created_at'],
    '%a %b %d %H:%M:%S +0000 %Y'
)

def tweet_favorite_count(tweet):
    try:
        rt_status = tweet['retweeted_status']
    except KeyError:
        return tweet['favorite_count']
    else:
        return rt_status['favorite_count']

TWITTER_STATUS_PATTERN = re.compile(r'http[s]?://twitter.com/\S+/status/(?P<status_id>\d+)')

PAST_FORMS = {
    'like':      'liked',
    'unlike':    'unliked',
    'retweet':   'retweeted',
    'unretweet': 'unretweeted',
    'reply to':  'replied to'
}

class Twitter(Plugin):

    def load(self):
        self.credentials = TwitterCredentials(
            self.config.get(c.CONSUMER_KEY_KEY),
            self.config.get(c.CONSUMER_SECRET_KEY),
            self.config.get(c.ACCESS_TOKEN_KEY),
            self.config.get(c.ACCESS_TOKEN_SECRET_KEY),
        )

        self.api = TwitterApi(self.credentials)

        context = dict(plugin=self, bot=self.bot)
        self.add_web_handlers(
            (r'/twitter/oauth_token', OAuthTokenHandler, context),
            (r'/twitter/authorize', OAuthAuthorizeHandler, context),
            (r'/twitter/status', TwitterStatusHandler, context),
            (r'/twitter/disconnect', TwitterDisconnectHandler, context),
        )

        self.monitored = set()
        self.restore_monitored()

        self.request_tokens = dict()
        self.last_tweets = dict()

        self.interactive_tweets = dict()

    def unload(self):
        self.monitored.clear()

    async def on_reaction_add(self, reaction, user):
        try:
            tweet = self.interactive_tweets[reaction.message.id]
        except KeyError:
            pass
        else:
            if reaction.emoji == '❤':
                await self.like_tweet(tweet, reaction.message.channel, user)
            elif reaction.emoji == '🔄':
                await self.rt_tweet(tweet, reaction.message.channel, user)

    async def on_reaction_remove(self, reaction, user):
        try:
            tweet = self.interactive_tweets[reaction.message.id]
        except KeyError:
            pass
        else:
            if reaction.emoji == '❤':
                await self.unlike_tweet(tweet, reaction.message.channel, user)
            elif reaction.emoji == '🔄':
                await self.unrt_tweet(tweet, reaction.message.channel, user)

    async def on_new(self, message):
        for match in TWITTER_STATUS_PATTERN.finditer(message.clean_content):
            status_id = match.group('status_id')
            tweet = await self.api.statuses.show(id=status_id, tweet_mode='extended')
            if tweet:
                await asyncio.sleep(2)
                await self.set_interactive_tweet(tweet, message)

    '''
    Commands
    '''

    twitter_prefix = p.string('!twitter')

    @command(
        twitter_prefix + p.string('last') + p.bind(p.word, 'screen_name')
    )
    async def last_tweet(self, message, screen_name):
        user = await self.get_user(screen_name=screen_name)
        self.debug(user['id'])
        tweets = await self.get_tweets(user['id'], count=5)

        # self.debug([tweet['full_text'] for tweet in tweets])
        if tweets:
            tweet = tweets[0]
            m = await self.send_interactive_tweet(
                message.channel,
                tweet,
                delete_after=150
            )
            self.last_tweets[message.channel.id] = tweet
            self.run_async(self.update_tweet(tweet, m))

    @command(
        twitter_prefix + p.string('monitor') + p.bind(p.word, 'screen_name'),
        master_only
    )
    async def monitor(self, message, screen_name):
        user = await self.get_user(screen_name=screen_name)
        user_id = user['id']

        with self.transaction() as trans:
            trans.execute(q.add_monitored, dict(
                user_id    = user_id,
                server_id  = message.server.id,
                channel_id = message.channel.id
            ))

            self.run_async(self.monitor_forever(user_id, message.channel))

            await self.send_message(
                message.channel,
                'Now monitoring `{}` tweets in this channel'.format(screen_name),
                delete_after=15
            )

    @command(
        twitter_prefix + p.string('unmonitor') + p.bind(p.word, 'screen_name'),
        master_only
    )
    async def unmonitor(self, message, screen_name):
        user = await self.get_user(screen_name=screen_name)
        user_id = user['id']

        if user_id not in self.monitored:
            return

        self.monitored.discard(user_id)

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

            user_futures = (
                self.get_user_by_id(channel.user_id)
                for channel in monitored
                if str(channel.server_id) == message.server.id
            )
            users = await asyncio.gather(*user_futures)

            await self.send_message(
                message.channel,
                'I\'m currently monitoring the following channels:\n{}'
                    .format(f.code_block(user['screen_name'] for user in users))
            )

    @command(p.string('!like'))
    async def like_tweet_command(self, message):
        try:
            tweet = self.last_tweets[message.channel.id]
        except KeyError:
            pass
        else:
            await self.like_tweet(tweet, message.channel, message.author)

    @command(p.string('!unlike'))
    async def unlike_tweet_command(self, message):
        try:
            tweet = self.last_tweets[message.channel.id]
        except KeyError:
            pass
        else:
            await self.unlike_tweet(tweet, message.channel, message.author)

    @command(p.string('!rt'))
    async def rt_tweet_command(self, message):
        try:
            tweet = self.last_tweets[message.channel.id]
        except KeyError:
            pass
        else:
            await self.rt_tweet(tweet, message.channel, message.author)

    @command(p.string('!unrt'))
    async def unrt_tweet_command(self, message):
        try:
            tweet = self.last_tweets[message.channel.id]
        except KeyError:
            pass
        else:
            await self.unrt_tweet(tweet, message.channel, message.author)

    @command(p.string('!reply'))
    async def reply_tweet(self, message):
        try:
            tweet = self.last_tweets[message.channel.id]
        except KeyError:
            pass
        else:
            # Replace emojis to avoid weird moon runes
            reply = re.sub(
                r'<:(.*):[0-9]+>',
                r'\1',
                message.clean_content[len('!reply'):].strip()
            )

            await self.twitter_three_legged_action(
                tweet, message.channel, message.author,
                lambda api, tweet: api.statuses.update(
                    status='@{} {}'.format(tweet['user']['screen_name'], reply),
                    in_reply_to_status_id=tweet['id'],
                    _method='POST'
                ),
                'reply to',
            )

    '''
    Details
    '''

    async def get_user(self, screen_name):
        try:
            users = await self.api.users.lookup(screen_name=screen_name)
            return users[0]
        except Exception:
            raise e.UserNotFound(screen_name)

    async def get_user_by_id(self, user_id):
        users = await self.api.users.lookup(user_id=user_id)
        return users[0]

    async def get_tweets(self, user_id, count):
        try:
            return await self.api.statuses.user_timeline(
                user_id=user_id,
                count=count,
                exclude_replies=True,
                tweet_mode='extended'
            )
        except Exception as e:
            self.error('Error retrieving {} tweets: {}'.format(user_id, e))
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
                self.run_async(self.monitor_forever(
                    channel.user_id,
                    server.get_channel(str(channel.channel_id))
                ))

    async def monitor_forever(self, user_id, channel):
        self.monitored.add(user_id)

        tweets = await self.get_tweets(user_id, count=1)
        if not tweets:
            self.error('NOT MONITORING TWEETS FOR {}'.format(user_id))
            return
        last_tweet = tweets[0]

        self.debug('Monitoring new tweets from {}'.format(user_id))

        while user_id in self.monitored:
            start = now()
            tweets = await self.get_tweets(user_id, count=5)
            self.debug(
                'took {:.3f} s to fetch tweets for {}: [{}]'
                    .format(now() - start, last_tweet['user']['screen_name'], 'OK' if tweets else 'FAIL')
            )
            if tweets:
                for tweet in sorted(tweets, key=tweet_time):
                    if tweet_time(tweet) > tweet_time(last_tweet):
                        last_tweet = tweet
                        m = await self.send_interactive_tweet(
                            channel,
                            tweet
                        )
                        self.last_tweets[channel.id] = tweet
                        self.run_async(self.update_tweet(tweet, m))
            await asyncio.sleep(45)

        self.debug('No longer monitoring {}'.format(user_id))

    async def send_interactive_tweet(self, channel, tweet, **kwargs):
        embed = await self.tweet_embed(tweet)
        message = await self.send_message(channel, '', embed=embed, **kwargs)

        await self.set_interactive_tweet(tweet, message)

        return message

    async def set_interactive_tweet(self, tweet, message):
        await self.bot.add_reaction(message, '🔄')
        await self.bot.add_reaction(message, '❤')

        self.interactive_tweets[message.id] = tweet

    async def update_tweet(self, tweet, message):
        for _ in range(10):
            await asyncio.sleep(20)
            try:
                tweet = await self.api.statuses.show(id=tweet['id'], tweet_mode='extended')
                embed = await self.tweet_embed(tweet)
                await self.bot.edit_message(message, '', embed=embed)
            except Exception as e:
                self.error(e)
                pass

    AUTHORIZE_CALLBACK = 'https://globibot.com/bot/twitter/authorize'
    def request_token(self, user):
        oauth = twitter.OAuth(
            self.credentials.access_token,
            self.credentials.access_token_secret,
            self.credentials.consumer_key,
            self.credentials.consumer_secret,
        )
        tweaked_twitter_client = twitter.Twitter(
            auth        = oauth,
            format      = '',
            api_version = None
        )

        try:
            response = tweaked_twitter_client.oauth.request_token(
                oauth_callback = Twitter.AUTHORIZE_CALLBACK
            )
        except Exception as e:
            self.error('Error while generating oauth token: {}'.format(e))
        else:
            params = dict(
                (key, value) for key, value in (
                    component.split('=')
                    for component in response.split('&')
                )
            )

            try:
                token = params['oauth_token']
                secret = params['oauth_token_secret']
            except:
                return
            else:
                self.info('Generated request token for {}'.format(user.name))
                self.request_tokens[token] = secret
                return token

    def save_user(self, user, oauth_token, oauth_verifier):
        oauth = twitter.OAuth(
            oauth_token,
            self.request_tokens[oauth_token],
            self.config.get(c.CONSUMER_KEY_KEY),
            self.config.get(c.CONSUMER_SECRET_KEY),
        )
        tweaked_twitter_client = twitter.Twitter(
            auth        = oauth,
            format      = '',
            api_version = None
        )

        try:
            response = tweaked_twitter_client.oauth.access_token(
                oauth_verifier = oauth_verifier
            )
        except Exception as e:
            self.error(e)
            pass
        else:
            params = dict(
                (key, value) for key, value in (
                    component.split('=')
                    for component in response.split('&')
                )
            )

            with self.transaction() as trans:
                trans.execute(q.add_user, dict(
                    id = user.id,
                    token = params['oauth_token'],
                    secret = params['oauth_token_secret']
                ))

    def disconnect_user(self, user):
        with self.transaction() as trans:
            trans.execute(q.delete_user, dict(id=user.id))

    def user_connected(self, user):
        with self.transaction() as trans:
            trans.execute(q.get_user, dict(id=user.id))

            if trans.fetchone():
                return True

        return False

    def get_user_oauth(self, user):
        with self.transaction() as trans:
            trans.execute(q.get_user, dict(id=user.id))

            data = trans.fetchone()
            if data:
                return OAuthUser(*data)

    def get_user_api(self, oauth_user):
        credentials = TwitterCredentials(
            self.config.get(c.CONSUMER_KEY_KEY),
            self.config.get(c.CONSUMER_SECRET_KEY),
            oauth_user.token,
            oauth_user.secret,
        )

        return TwitterApi(credentials)

    async def like_tweet(self, tweet, channel, user):
        await self.twitter_three_legged_action(
            tweet, channel, user,
            lambda api, tweet: api.favorites.create(_id=tweet['id']),
            'like',
        )

    async def unlike_tweet(self, tweet, channel, user):
        await self.twitter_three_legged_action(
            tweet, channel, user,
            lambda api, tweet: api.favorites.destroy(_id=tweet['id']),
            'unlike',
        )

    async def rt_tweet(self, tweet, channel, user):
        await self.twitter_three_legged_action(
            tweet, channel, user,
            lambda api, tweet: api.statuses.retweet(id=tweet['id'], _method='POST'),
            'retweet',
        )

    async def unrt_tweet(self, tweet, channel, user):
        await self.twitter_three_legged_action(
            tweet, channel, user,
            lambda api, tweet: api.statuses.unretweet(id=tweet['id'], _method='POST'),
            'unretweet',
        )

    async def inform_user_about_connections(self, user):
        await self.send_message(
            user,
            'Psst\nI noticed that you tried using a special Twitter command\n'
            'This command requires me to manipulate a limited scope of '
            'your Twitter account\n'
            'If you trust me enough to do so, please go to '
            'https://globibot.com/#connections to connect your Twitter acount'
        )

    async def twitter_three_legged_action(self, tweet, channel, user, action, description):
        oauth_user = self.get_user_oauth(user)

        if oauth_user is None:
            await self.inform_user_about_connections(user)
            return

        user_api = self.get_user_api(oauth_user)

        try:
            await action(user_api, tweet)
        except Exception as e:
            await self.send_message(
                user,
                'I couldn\'t {} `{}`\'s tweet for you\n'
                'Twitter said:\n{}'
                    .format(
                        description,
                        tweet['user']['screen_name'],
                        f.code_block(str(e.response_data))
                    )
            )
        else:
            await self.send_message(
                channel,
                '{} I {} `{}`\'s tweet for you 👍'
                    .format(
                        user.mention,
                        PAST_FORMS[description],
                        tweet['user']['screen_name']
                    ),
                delete_after = 5
            )

    async def replies_to_tweet(self, tweet):
        screen_name = tweet['user']['screen_name']
        query = '@{}'.format(screen_name)

        try:
            result = await self.api.search.tweets(q=query, since_id=tweet['id'])
            statuses = result['statuses']
        except Exception as e:
            self.debug('Error fetching replies: {}'.format(e))
            return []
        else:
            return [
                status for status in statuses
                if status['in_reply_to_status_id'] == tweet['id']
            ]

    async def tweet_embed(self, tweet):
        name = tweet['user']['name']
        screen_name = tweet['user']['screen_name']

        body = '{text}\n\n🔄 **{rts}** ❤ **{likes}**'.format(
            text  = tweet['full_text'],
            rts   = tweet['retweet_count'],
            likes = tweet_favorite_count(tweet)
        )
        embed = Embed(
            title       = 'Latest tweet',
            description = body,
            url         = 'https://twitter.com/{}/status/{}'.format(screen_name, tweet['id']),
        )
        embed.set_author(
            name     = name,
            icon_url = 'https://twitter.com/favicon.ico',
            url      = 'https://twitter.com/{}'.format(screen_name)
        )
        embed.set_thumbnail(url=tweet['user']['profile_image_url_https'])
        embed.colour = 0x1da1f2
        embed.set_footer(text='Click the reactions below to like or retweet')
        embed.timestamp = tweet_time(tweet)

        try:
            entities = tweet['extended_entities']['media']
            media_urls = [entity['media_url_https'] for entity in entities]
        except:
            pass
        else:
            embed.set_image(url=media_urls[0])

        replies = await self.replies_to_tweet(tweet)
        if replies:
            embed.add_field(
                name  = 'Latest replies',
                value = '\n'.join(format_reply(reply, tweet) for reply in replies[:3])
            )

        return embed

def format_reply(reply, tweet):
    screen_name = reply['user']['screen_name']
    link = 'https://twitter.com/{}'.format(screen_name)
    reply_mention = '@{}'.format(tweet['user']['screen_name'])
    text = reply['text'].replace(reply_mention, '').strip()

    return '[@{screen_name:10.10}]({link}): {text}'.format(
        screen_name = screen_name,
        link        = link,
        text        = text
    )
