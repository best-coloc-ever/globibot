from globibot.lib.web.handlers import SessionHandler
from globibot.lib.web.decorators import authenticated, respond_json

from http import HTTPStatus

server_data = lambda server: dict(
    id       = server.id,
    name     = server.name,
    icon_url = server.icon_url,
)

class GuildHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self, server_id):
        server = self.bot.find_server(server_id)
        if server:
            return server_data(server)
        else:
            self.set_status(HTTPStatus.BAD_REQUEST)
