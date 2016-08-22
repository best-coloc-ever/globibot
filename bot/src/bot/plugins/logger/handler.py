from tornado.web import RequestHandler
from tornado.escape import json_encode

from collections import defaultdict

from . import queries as q

class LogsStaticHandler(RequestHandler):

    async def get(self, test):
        with open('src/bot/plugins/logger/html/{}'.format(test)) as f:
            self.write(f.read())

class LogsTopHandler(RequestHandler):

    async def get(self):
        with open('src/bot/plugins/logger/html/top/index.html') as f:
            self.write(f.read())

class LogsUserHandler(RequestHandler):

    async def get(self):
        with open('src/bot/plugins/logger/html/user/index.html') as f:
            self.write(f.read())

class Cache:

    def __init__(self):
        self.member_caches = defaultdict(dict)

    def member(self, server, user_id):
        try:
            return self.member_caches[server.id][user_id]
        except KeyError:
            member = server.get_member(user_id)
            if member:
                self.member_caches[server.id][user_id] = member
                return member

cache = Cache()

class LogsApiTopHandler(RequestHandler):

    def initialize(self, plugin):
        self.plugin = plugin

    def get(self, server_id):
        server = next(server for server in self.plugin.bot.servers if server.id == server_id)

        with self.plugin.transaction() as trans:
            trans.execute(q.most_logs, dict(
                server_id = server_id,
                limit     = 1000
            ))

            results = []
            for r in trans.fetchall():
                user_id = str(r[0])
                member = cache.member(server, user_id)
                if member:
                    results.append(((user_id, member.name), r[1], r[2].timestamp()))

            self.set_header("Content-Type", 'application/json')
            self.write(json_encode(results))

class LogsApiUserHandler(RequestHandler):

    def initialize(self, plugin):
        self.plugin = plugin

    def get(self, user_id):
        with self.plugin.transaction() as trans:
            content = '''
                select content, stamp from log
                    where   author_id = %(author_id)s
            '''
            trans.execute(content, dict(
                author_id = user_id,
            ))

            self.set_header("Content-Type", 'application/json')
            self.write(json_encode([(r[0], r[1].timestamp()) for r in trans.fetchall()]))
