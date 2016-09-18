from globibot.lib.web.handlers import SessionHandler
from globibot.lib.web.decorators import authenticated, respond_json, with_body_arguments

from .giveaway import Giveaway

def server_data(server):
    return dict(
        id       = server.id,
        name     = server.name,
        icon_url = server.icon_url
    )

class GiveawayInfo(SessionHandler):

    @authenticated
    @respond_json
    def get(self):
        user = self.current_user
        return dict(
            giveaway_count = self.plugin.giveaways_left_for(user),
            servers = [server_data(s) for s in self.bot.servers_of(user)]
        )

class GiveawayStart(SessionHandler):

    @authenticated
    @respond_json
    @with_body_arguments('server_id', 'title', 'content')
    def post(self, server_id, title, content):
        user = self.current_user
        server = self.bot.find_server(server_id)
        if server is None:
            return

        giveaway = Giveaway(
            user    = user,
            server  = server,
            title   = title,
            content = content,
            timeout = 120
        )

        if self.plugin.start_giveaway(giveaway):
            message = 'Giveaway started'
        else:
            message = 'There is a giveaway in progress, try again later'

        return dict(message = message)
