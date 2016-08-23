from bot.lib.plugin import Plugin
# from bot.lib.decorators import command
# from bot.lib.helpers import parsing as p
from bot.lib.helpers import formatting as f
# from bot.lib.helpers.hooks import master_only

from .handler import RepostStaticHandler, RepostHandler, RepostAPIHandler

from collections import defaultdict
from datetime import datetime
from time import time

import re

URL_PATTERN = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

class Repost(Plugin):

    def load(self):
        self.links = self.load_links()

        self.add_web_handlers(
            (r'/repost/api/(?P<server_id>\w+)', RepostAPIHandler, dict(plugin=self)),
            (r'/repost', RepostHandler),
            (r'/repost/(.*)', RepostStaticHandler),
        )

    async def on_new(self, message):
        for url in URL_PATTERN.findall(message.content):
            try:
                author_id, stamp = self.links[message.server.id][url]
                await self.send_message(
                    message.channel,
                    '🔔 {} you posted a link originally posted by {} ({} UTC) 🔔\nPlease visit {} for more information'
                        .format(
                            message.author.mention,
                            f.mention(author_id),
                            datetime.fromtimestamp(stamp).strftime('%m-%e-%y %H:%M'),
                            'https://globibot.com/repost?id={}'.format(message.server.id)
                        ),
                    delete_after = 30
                )
            except KeyError:
                self.links[message.server.id][url] = (message.author.id, time())

    def load_links(self):
        links = defaultdict(dict)

        with self.transaction() as trans:
            trans.execute('''
                select      author_id, stamp, server_id, content
                from        log
                order by    stamp desc
            ''')

            for author_id, stamp, server_id, content in trans.fetchall():
                for url in URL_PATTERN.findall(content):
                    links[str(server_id)][url] = (str(author_id), stamp.timestamp())

        return links
