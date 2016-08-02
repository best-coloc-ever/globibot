from bot.lib.module import Module

from .handler import StatsServersHandler
from .ws_handler import StatsWebSocketHandler

from collections import defaultdict

class Stats(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        context = {
            'module': self
        }
        self.bot.web.add_handlers(r'.*$', [
            (r'/servers', StatsServersHandler, context),
            (r'/servers/([0-9]+)', StatsServersHandler, context),
            (r'/ws', StatsWebSocketHandler, context),
        ])

        self.messages_per_server = defaultdict(list)
        self.ws_consumers = set()

    async def on_message(self, message):
        data = {
            'server': {
                'name': message.server.name,
                'id': message.server.id,
            },
            'channel': {
                'name': message.channel.name,
                'id': message.channel.id,
            },
            'author': {
                'name': message.author.name,
                'id': message.author.id,
            },
            'content': message.content,
        }

        self.messages_per_server[message.server.id].append(data)
        for consumer in self.ws_consumers:
            consumer.write_message(data)
