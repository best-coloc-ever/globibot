from bot.lib.module import Module

from .handler import StatsHandler

from collections import defaultdict

class Stats(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot.web.add_handlers(r'.*$', [
            (r'/stats/([0-9]+)', StatsHandler, dict(module=self))
        ])

        self.messages_per_server = defaultdict(list)

    def on_message(self, message):
        self.messages_per_server[message.server.id].append({
            'author': {
                'name': message.author.name,
                'id': message.author.id,
            },
            'content': message.content
        })
