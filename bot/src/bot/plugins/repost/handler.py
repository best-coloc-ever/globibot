from tornado.web import RequestHandler
from tornado.escape import json_encode

class RepostStaticHandler(RequestHandler):

    async def get(self, test):
        with open('src/bot/plugins/repost/html/{}'.format(test)) as f:
            self.write(f.read())

class RepostHandler(RequestHandler):

    async def get(self):
        with open('src/bot/plugins/repost/html/index.html') as f:
            self.write(f.read())

class RepostAPIHandler(RequestHandler):

    def initialize(self, plugin):
        self.plugin = plugin

    async def get(self, server_id):
        self.set_header("Content-Type", 'application/json')
        self.write(json_encode(self.plugin.links[server_id]))

class RepostAPIShamesHandler(RequestHandler):

    def initialize(self, plugin):
        self.plugin = plugin

    async def get(self, server_id):
        self.set_header("Content-Type", 'application/json')
        self.write(json_encode(self.plugin.shames[server_id]))
