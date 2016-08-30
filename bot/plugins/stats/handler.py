from tornado.web import RequestHandler
from tornado.escape import json_encode

from collections import namedtuple, defaultdict

from time import time

class StatsStaticHandler(RequestHandler):

    async def get(self, test):
        with open('./plugins/stats/html/{}'.format(test)) as f:
            self.write(f.read())

class StatsUserHandler(RequestHandler):

    async def get(self):
        with open('./plugins/stats/html/user_top/index.html') as f:
            self.write(f.read())

class StatsGameHandler(RequestHandler):

    async def get(self):
        with open('./plugins/stats/html/game_top/index.html') as f:
            self.write(f.read())

class Cache:

    def __init__(self):
        self.member_caches = defaultdict(dict)
        self.cache = dict()
        self.last_update = 0

    def get_data(self, server, plugin):
        now = time()
        if now - self.last_update > 300:
            self.last_update = now
            data = plugin.top_games(server, 1000)
            data = [
                d[:3] + ((str(d[3]), self.member(server, str(d[3])).name),)
                for d in data
            ]
            self.cache[server.id] = data

        return self.cache.get(server.id)

    def member(self, server, user_id):
        try:
            return self.member_caches[server.id][user_id]
        except KeyError:
            member = server.get_member(user_id)
            if member:
                self.member_caches[server.id][user_id] = member
                return member

cache = Cache()

TopGame = namedtuple('TopGame', ['name', 'playtime', 'count', 'most'])
class StatsGamesTopHandler(RequestHandler):

    def initialize(self, plugin):
        self.plugin = plugin

    async def get(self, server_id):
        server = next(server for server in self.plugin.bot.servers if server.id == server_id)
        data = cache.get_data(server, self.plugin)
        if data:
            top_games = [TopGame(*row) for row in data]
            self.set_header("Content-Type", 'application/json')
            self.write(json_encode(top_games))


class StatsGamesUserHandler(RequestHandler):

    def initialize(self, plugin):
        self.plugin = plugin

    async def get(self, user_id):
        data = self.plugin.top_user_games(user_id)
        self.plugin.debug(data)
        if data:
            what = [(game.name, game.duration) for game in data]
            self.set_header("Content-Type", 'application/json')
            self.write(json_encode(what))
