from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command
from globibot.lib.helpers import parsing as p
from globibot.lib.helpers.hooks import master_only

from instagram.client import InstagramAPI

from . import constants as c

import random

class Instagram(Plugin):

    def load(self):
        access_token = self.config.get(c.ACCESS_TOKEN_KEY)
        client_secret = self.config.get(c.CLIENT_SECRET_KEY)
        self.api = InstagramAPI(
            access_token  = access_token,
            client_secret = client_secret
        )

    @command(p.string('!instagram') + p.bind(p.word, 'channel'), master_only)
    async def last_pic(self, message, channel):
        users = self.api.user_search(channel)
        if users:
            user = users[0]
            media, _ = self.api.user_recent_media(user_id=user.id, count=10)
            medium = random.choice(media)
            await self.send_message(
                message.channel,
                'A media from `{}`\'s instagram\n{}'
                    .format(user.full_name, medium.images['standard_resolution'].url),
                delete_after = 30
            )

