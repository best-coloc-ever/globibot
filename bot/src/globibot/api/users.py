from globibot.lib.web.handlers import ContextHandler, SessionHandler
from globibot.lib.web.decorators import authenticated, respond_json, with_query_parameters

from http import HTTPStatus

user_data = lambda user: dict(
    id         = user.id,
    name       = user.name,
    avatar_url = user.avatar_url,
)

class UserHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self, user_id):
        user = self.bot.find_user(user_id)
        if user:
            return user_data(user)
        else:
            self.set_status(HTTPStatus.BAD_REQUEST)

class UserSelfHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self):
        return user_data(self.current_user)

class UserFindHandler(ContextHandler):

    @respond_json
    @with_query_parameters('user_name')
    def get(self, user_name):
        user = self.bot.find_user_by_name(user_name)
        if user:
            return user_data(user)
        else:
            self.set_status(HTTPStatus.BAD_REQUEST)
