from tornado.web import RequestHandler
from tornado.escape import json_encode

class StatsHandler(RequestHandler):

    def initialize(self, module):
        self.module = module

    async def get(self, server_id):
        self.set_header('Content-Type', 'application/json')
        messages = self.module.messages_per_server[server_id]
        self.write(json_encode(messages))
