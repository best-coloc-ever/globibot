from tornado.web import RequestHandler
from tornado.escape import json_encode

from discord import ChannelType

class StatsServersHandler(RequestHandler):

    def initialize(self, module):
        self.module = module

    async def get(self, server_id=None):
        self.set_header('Content-Type', 'application/json')
        if server_id is None:
            await self.list_servers()
        else:
            await self.list_channels(server_id)

    async def list_servers(self):
        servers = [
            {
                'id': server.id,
                'name': server.name,
            }
            for server in self.module.bot.enabled_servers
        ]
        self.write(json_encode(servers))

    async def list_channels(self, server_id):
        try:
            server = next(
                server for server in self.module.bot.enabled_servers
                if server.id == server_id
            )
        except StopIteration:
            self.set_status(404)
        else:
            channels = [
                {
                    'id': channel.id,
                    'name': channel.name,
                }
                for channel in sorted(server.channels, key=lambda s: s.position)
                if channel.type == ChannelType.text
            ]
            self.write(json_encode(channels))
