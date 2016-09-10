from globibot.lib.web.handlers import SessionHandler
from globibot.lib.web.decorators import authenticated, respond_json

from . import queries as q

class LogsApiTopHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self):
        servers = self.bot.servers_of(self.current_user)

        with self.plugin.transaction() as trans:
            trans.execute(q.most_logs, dict(
                server_id = servers[0].id,
                limit     = 200
            ))

            results = dict(server_id=servers[0].id, data=[])
            for r in trans.fetchall():
                user_id = str(r[0])
                member = self.bot.find_user(user_id)
                if member:
                    results['data'].append(((user_id, member.name), r[1], r[2].timestamp()))

            return results

class LogsApiUserHandler(SessionHandler):

    @authenticated
    @respond_json
    def get(self, user_id):
        with self.plugin.transaction() as trans:
            content = '''
                select content, stamp from log
                    where   author_id = %(author_id)s
            '''
            trans.execute(content, dict(
                author_id = user_id,
            ))

            return [(r[0], r[1].timestamp()) for r in trans.fetchall()]
