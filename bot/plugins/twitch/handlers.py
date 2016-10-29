from globibot.lib.web.handlers import SessionHandler
from globibot.lib.web.decorators import authenticated, respond_json, \
    respond_json_async, with_query_parameters, with_body_arguments

from urllib.parse import urlencode

class OAuthRequestTokenHandler(SessionHandler):

    BASE_URL = 'https://api.twitch.tv/kraken/oauth2/authorize'
    AUTHORIZE_CALLBACK = 'https://globibot.com/bot/twitch/authorize'
    SCOPES = ['user_follows_edit', 'user_subscriptions', 'chat_login', 'user_read']

    @authenticated
    def get(self):
        state = self.plugin.request_token_state(self.current_user)

        params = urlencode((
            ('response_type', 'code'),
            ('client_id', self.plugin.client_id),
            ('redirect_uri', OAuthRequestTokenHandler.AUTHORIZE_CALLBACK),
            ('scope', ' '.join(OAuthRequestTokenHandler.SCOPES)),
            ('state', state)
        ))
        url = '{}?{}'.format(OAuthRequestTokenHandler.BASE_URL, params)

        self.redirect(url)

class OAuthAuthorizeHandler(SessionHandler):

    @authenticated
    @with_query_parameters('code', 'state')
    async def get(self, code, state):
        await self.plugin.save_user(self.current_user, code, state)

        self.redirect('/#connections')

class TwitchStatusHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self):
        return dict(
            connected = self.plugin.user_connected(self.current_user)
        )

class TwitchFollowedHandler(SessionHandler):

    @authenticated
    @respond_json_async
    async def get(self):
        followed, monitored = await self.plugin.user_followed(self.current_user)

        return dict(
            followed = followed,
            monitored = monitored
        )

class TwitchDisconnectHandler(SessionHandler):

    @authenticated
    @respond_json
    def post(self):
        self.plugin.disconnect_user(self.current_user)

        return dict(status='ok')

class TwitchMentionHandler(SessionHandler):

    @authenticated
    @respond_json
    @with_body_arguments('channel', 'state')
    def post(self, channel, state):
        self.plugin.user_notify_mention(
            self.current_user,
            channel,
            state == 'true'
        )

        return dict(status='ok')

class TwitchWhisperHandler(SessionHandler):

    @authenticated
    @respond_json_async
    @with_body_arguments('channel', 'state')
    async def post(self, channel, state):
        await self.plugin.user_notify_whisper(
            self.current_user,
            channel,
            state == 'true'
        )

        return dict(status='ok')
