from globibot.lib.web.handlers import SessionHandler
from globibot.lib.web.decorators import authenticated, respond_json, with_query_parameters

class OAuthTokenHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self):
        token = self.plugin.request_token(self.current_user)

        if token:
            return dict(token=token)


class OAuthAuthorizeHandler(SessionHandler):

    @authenticated
    @with_query_parameters('oauth_token', 'oauth_verifier')
    def get(self, oauth_token, oauth_verifier):
        self.plugin.save_user(self.current_user, oauth_token, oauth_verifier)

        self.redirect('/#connections')

class TwitterStatusHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self):
        return dict(
            connected = self.plugin.user_connected(self.current_user)
        )

class TwitterDisconnectHandler(SessionHandler):

    @authenticated
    @respond_json
    def post(self):
        self.plugin.disconnect_user(self.current_user)

        return dict(status='ok')
