from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command
from globibot.lib.helpers import parsing as p

from collections import defaultdict
from datetime import datetime
from time import time

import re

URL_PATTERN = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

LIRIK_SERVER_ID = '84822922958487552'
LOG_CHANNEL_ID = '235899097930924032'

LINK_COOLDOWN = 5

class Gav(Plugin):

    def load(self):
        self.handlers = dict(
            on_member_join   = self.on_member_join,
            on_member_remove = self.on_member_remove,
            on_member_ban    = self.on_member_ban,
            on_member_unban  = self.on_member_unban,
        )

        server = self.bot.find_server(LIRIK_SERVER_ID)

        self.server = server
        self.channel = next(
            channel for channel in server.channels
            if channel.id == LOG_CHANNEL_ID
        )

        self.mod_role = next(
            role for role in server.roles
            if role.id == '98596789229228032'
        )

        self.post_timer = defaultdict(lambda: 0)

    @command(p.string('!birth') + p.bind(p.maybe(p.mention), 'user'))
    async def birth(self, message, user=None):
        user = message.author if user is None else self.bot.find_user(str(user))
        days = (datetime.utcnow() - user.created_at).days
        await self.send_message(
            message.channel,
            f'{message.author.mention} {user.created_at} `~{days} days ago`'
        )

    async def on_new(self, message):
        if message.channel == self.server.default_channel:
            # whitelist mods
            if self.mod_role in message.author.roles:
                return
            await self.check_post(message)

    async def on_raw_event(self, event, *args, **kwargs):
        try:
            handler = self.handlers[event]
            await handler(*args, **kwargs)
        except KeyError:
            pass

    async def on_member_join(self, member):
        if member.server.id != LIRIK_SERVER_ID:
            return

        await self.log_activity('JOIN', member)

    async def on_member_remove(self, member):
        if member.server.id != LIRIK_SERVER_ID:
            return

        await self.log_activity('LEAVE', member)

    async def on_member_ban(self, member):
        if member.server.id != LIRIK_SERVER_ID:
            return

        await self.log_activity('BAN', member)

    async def on_member_unban(self, server, user):
        if server.id != LIRIK_SERVER_ID:
            return

        await self.log_activity('UNBAN', user)

    async def log_activity(self, what, who):
        data = dict(
            stamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            user_name = who.name,
            mention = who.mention,
            what = what
        )

        await self.send_message(
            self.channel,
            '`[{stamp}] [{what: <5}] {user_name: <20}·` {mention}'
                .format(**data)
        )

    async def check_post(self, message):
        if message.attachments or URL_PATTERN.search(message.clean_content):
            now = time()
            if now - self.post_timer[message.author.id] <= LINK_COOLDOWN:
                await self.bot.delete_message(message)
                await self.send_message(
                    message.author,
                    'As part of a moderators\' request on the server `{}` to '
                    'help prevent spam, I deleted your last message in `#{}` '
                    'because it contained **links** or **attachments** and was '
                    'sent too briefly after the previous link or attachment.\n'
                    'You will be able to post your message again in `{:.2f}` seconds.\n'
                    'Cheers ❤'
                        .format(
                            message.server.name,
                            message.channel.name,
                            LINK_COOLDOWN - (now - self.post_timer[message.author.id])
                        )
                )
            else:
                self.post_timer[message.author.id] = now
