from globibot.lib.web.handlers import SessionHandler
from globibot.lib.web.decorators import authenticated, respond_json

from . import queries as q

def user_data(user_snowflake, server):
    data = dict(id=user_snowflake)
    member = server.get_member(user_snowflake)
    if member:
        data = {
            **data,
            **dict(
                name       = member.name,
                avatar_url = member.avatar_url
            )
        }
    return data

def channel_data(channel):
    if channel:
        return dict(
            id   = channel.id,
            name = channel.name,
        )

def server_data(server):
    if server:
        return dict(
            id       = server.id,
            name     = server.name,
            icon_url = server.icon_url
        )

class LogsApiTopHandler(SessionHandler):

    USER_COUNT_LIMIT = 150

    @authenticated
    @respond_json
    def get(self):
        return [
            self.server_data(server)
            for server in self.bot.servers_of(self.current_user)
        ]

    def server_data(self, server):
        with self.plugin.transaction() as trans:
            trans.execute(q.most_logs, dict(
                server_id = server.id,
                limit     = LogsApiTopHandler.USER_COUNT_LIMIT
            ))

            return dict(
                server_id = server.id,
                data = [
                    dict(
                        user        = user_data(str(user_id), server),
                        count       = count,
                        last_active = last_active.timestamp()
                    )
                    for user_id, count, last_active in trans.fetchall()
                ]
            )

class LogsApiUserHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self, user_id):
        user_servers = self.bot.servers_of(self.current_user)
        find_server = lambda id: next((s for s in user_servers if s.id == str(id)), None)
        def find_channel(id, server_id):
            server = find_server(server_id)
            if server:
                return server.get_channel(str(id))

        with self.plugin.transaction() as trans:
            trans.execute(q.user_content, dict(
                author_id  = user_id,
                server_ids = tuple(server.id for server in user_servers)
            ))

            return [
                dict (
                    id         = log_id,
                    channel    = channel_data(find_channel(channel_id, server_id)),
                    server     = server_data(find_server(server_id)),
                    content    = content,
                    is_deleted = is_deleted,
                    stamp      = date.timestamp()
                )
                for log_id, channel_id, server_id, content, is_deleted, date
                in trans.fetchall()
            ]
