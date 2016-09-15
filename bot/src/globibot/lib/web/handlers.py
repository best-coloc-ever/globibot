from tornado.web import RequestHandler

from . import constants as c

class ContextHandler(RequestHandler):

    def initialize(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

class SessionHandler(ContextHandler):

    def get_current_user(self):
        cookie = self.get_secure_cookie(c.USER_COOKIE_NAME)

        if cookie:
            user_id = cookie.decode('ascii')
            return self.bot.find_user(user_id)
