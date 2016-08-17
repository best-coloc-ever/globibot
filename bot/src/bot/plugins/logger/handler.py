from tornado.web import RequestHandler
from tornado.escape import json_encode

from collections import namedtuple, defaultdict

from time import time

from . import queries as q

class LogsStaticHandler(RequestHandler):

    async def get(self, test):
        with open('src/bot/plugins/logger/html/{}'.format(test)) as f:
            self.write(f.read())

class LogsHandler(RequestHandler):

    async def get(self):
        with open('src/bot/plugins/logger/html/index.html') as f:
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
                member = cache.member(server, str(r[0]))
                if member:
                    results.append((member.name, r[1]))

            self.set_header("Content-Type", 'application/json')
            self.write(json_encode(results))
