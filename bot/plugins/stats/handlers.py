from globibot.lib.web.handlers import SessionHandler
from globibot.lib.web.decorators import authenticated, respond_json, with_query_parameters

class GamesTopHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self):
        return [
            dict(
                server_id = server.id,
                stats     = [
                    dict(
                        name     = name,
                        duration = duration,
                        playing  = playing
                    )
                    for name, duration, playing in self.plugin.top_games(server, 100)
                ],
            )
            for server in self.bot.servers_of(self.current_user)
        ]

def user_data(user_snowflake, servers):
    data = dict(id=user_snowflake)

    for server in servers:
        member = server.get_member(str(user_snowflake))
        if member:
            data = {
                **data,
                **dict(
                    name       = member.name,
                    avatar_url = member.avatar_url
                )
            }
            break

    return data

def in_servers(user_id, servers):
    for server in servers:
        if server.get_member(str(user_id)):
            return True

    return False

class GameStatsHandler(SessionHandler):

    @authenticated
    @respond_json
    @with_query_parameters('name')
    def get(self, name):
        servers = self.bot.servers_of(self.current_user)

        return [
            dict(
                user = user_data(str(user_id), servers),
                duration = duration
            )
            for user_id, duration
            in self.plugin.top_users(name, 1000)
            if in_servers(user_id, servers)
        ]

class GameUserHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self, user_id):
        self.plugin.debug([
            dict(
                name = game_played.name,
                duration = game_played.duration,
            )
            for game_played in self.plugin.top_user_games(user_id)
        ])
        return [
            dict(
                name = game_played.name,
                duration = game_played.duration,
            )
            for game_played in self.plugin.top_user_games(user_id)
        ]
