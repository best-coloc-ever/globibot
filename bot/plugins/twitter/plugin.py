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

from twitter import Twitter as TwitterAPI
from twitter import OAuth

from random import randint
from humanize import naturaltime
from datetime import datetime
from collections import namedtuple

from discord import Embed, Color

import asyncio
import re

MonitoredChannel = namedtuple(
    'MonitoredChannel',
    ['id', 'user_id', 'server_id']
)

OAuthUser = namedtuple(
    'OAuthUser',
    ['token', 'secret']
)

tweet_time = lambda tweet: datetime.strptime(
    tweet['created_at'],
    '%a %b %d %H:%M:%S +0000 %Y'
)

TWITTER_STATUS_PATTERN = re.compile(r'http[s]?://twitter.com/\S+/status/(?P<status_id>\d+)')

PAST_FORMS = {
    'like':      'liked',
    'unlike':    'unliked',
    'retweet':   'retweeted',
    'unretweet': 'unretweeted',
    'reply to':  'replied to'
}

def tweet_embed(tweet):
    screen_name = tweet['user']['screen_name']

    embed = Embed(
        title       = 'Latest tweet from {}'.format(screen_name),
        description = tweet['text'],
        url         = 'https://twitter.com/{}/status/{}'.format(screen_name, tweet['id']),
    )
    embed.colour = randint(0, 0xffffff)
    embed.timestamp = tweet_time(tweet)
    embed.set_thumbnail(url=tweet['user']['profile_image_url_https'])
    embed.provider.name = 'Twitter'
    embed.provider.url = 'https://twitter.com'

    try:
        entities = tweet['extended_entities']['media']
        media_urls = [entity['media_url_https'] for entity in entities]
    except:
        pass
    else:
        embed.set_image(url=media_urls[0])

    return embed

class Twitter(Plugin):

    def load(self):
        self.oauth = OAuth(
            self.config.get(c.ACCESS_TOKEN_KEY),
            self.config.get(c.ACCESS_TOKEN_SECRET_KEY),
            self.config.get(c.CONSUMER_KEY_KEY),
            self.config.get(c.CONSUMER_SECRET_KEY),
        )

        self.client = TwitterAPI(auth=self.oauth)

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
            tweet = self.client.statuses.show(id=status_id)
            if tweet:
                await asyncio.sleep(2)
                await self.set_interactive_tweet(tweet, message)

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
                        m = await self.send_interactive_tweet(
                            server.default_channel,
                            latest
                        )
                        self.last_tweets[server.default_channel.id] = latest
                        self.run_async(self.update_tweet(latest, m))

        self.debug('No longer monitoring {}'.format(user_id))

    async def send_interactive_tweet(self, channel, tweet, **kwargs):
        message = await self.send_message(channel, '', embed=tweet_embed(tweet), **kwargs)

        await self.set_interactive_tweet(tweet, message)

        return message

    async def set_interactive_tweet(self, tweet, message):
        await self.bot.add_reaction(message, '🔄')
        await self.bot.add_reaction(message, '❤')

        self.interactive_tweets[message.id] = tweet

    async def update_tweet(self, tweet, message):
        for i in range(10):
            await asyncio.sleep(20)
            try:
                tweet = self.client.statuses.show(id=tweet['id'])
                await self.edit_message(message, '', embed=tweet_embed(tweet))
            except Exception as e:
                self.error(e)
                pass

    AUTHORIZE_CALLBACK = 'https://globibot.com/bot/twitter/authorize'
    def request_token(self, user):
        tweaked_twitter_client = TwitterAPI(
            auth        = self.oauth,
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
        oauth = OAuth(
            oauth_token,
            self.request_tokens[oauth_token],
            self.config.get(c.CONSUMER_KEY_KEY),
            self.config.get(c.CONSUMER_SECRET_KEY),
        )
        tweaked_twitter_client = TwitterAPI(
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
        oauth = OAuth(
            oauth_user.token,
            oauth_user.secret,
            self.config.get(c.CONSUMER_KEY_KEY),
            self.config.get(c.CONSUMER_SECRET_KEY),
        )

        return TwitterAPI(auth = oauth)

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
            action(user_api, tweet)
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
