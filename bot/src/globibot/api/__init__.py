from .auth import LoginHandler, RegistrationHandler, RegistrationTokenHandler
from .users import UserHandler, UserSelfHandler, UserFindHandler
from .guilds import GuildHandler

ROUTE_DESCRIPTORS = (
    (r'/api/login',                 LoginHandler),
    (r'/api/register',              RegistrationHandler),
    (r'/api/send-registration-token/(?P<user_id>\d+)',
                                    RegistrationTokenHandler),

    (r'/api/user',                  UserSelfHandler),
    (r'/api/user/(?P<user_id>\d+)', UserHandler),
    (r'/api/find',                  UserFindHandler),

    (r'/api/server/(?P<server_id>\d+)',
                                    GuildHandler),
)

def routes(bot):
    context = dict(bot = bot)

    mk_route = lambda pattern, handler: (pattern, handler, context)

    return [
        mk_route(*route_descriptor)
        for route_descriptor in ROUTE_DESCRIPTORS
    ]
