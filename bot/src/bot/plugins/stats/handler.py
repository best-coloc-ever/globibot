from tornado.web import RequestHandler
from tornado.escape import json_encode

from collections import namedtuple, defaultdict

class StatsStaticHandler(RequestHandler):

    async def get(self, test):
        with open('src/bot/plugins/stats/html/{}'.format(test)) as f:
            self.write(f.read())

class StatsGameHandler(RequestHandler):

    async def get(self):
        with open('src/bot/plugins/stats/html/index.html') as f:
            self.write(f.read())

TopGame = namedtuple('TopGame', ['name', 'playtime', 'count', 'most'])
class StatsGamesTopHandler(RequestHandler):

    def initialize(self, plugin):
        self.plugin = plugin
        self.member_caches = defaultdict(dict)

    def member(self, server, user_id):
        try:
            return self.member_caches[server.id][user_id]
        except KeyError:
            member = server.get_member(user_id)
            if member:
                self.member_caches[server.id][user_id] = member
                return member

    async def get(self, server_id):
        server = next(server for server in self.plugin.bot.servers if server.id == server_id)
        data = self.plugin.top_games(server, 1000)
        data = [
            d[:3] + (self.member(server, str(d[3])).name,)
            for d in data
        ]
        if data:
            top_games = [TopGame(*row) for row in data]
            self.set_header("Content-Type", 'application/json')
            self.write(json_encode(top_games))
