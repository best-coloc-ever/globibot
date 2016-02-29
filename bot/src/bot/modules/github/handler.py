from tornado.web import RequestHandler
from tornado.escape import json_decode

class GithubHandler(RequestHandler):

    def initialize(self, module):
        self.module = module

    async def post(self):
        data = json_decode(self.request.body)
        event_type = self.request.headers['X-Github-Event']

        await self.module.github_notification(event_type, data)
