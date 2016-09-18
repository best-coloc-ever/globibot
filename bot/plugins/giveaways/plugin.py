from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command
from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f

from random import choice
from collections import defaultdict

from . import constants as c
from .handlers import GiveawayInfo, GiveawayStart

import asyncio

class Giveaways(Plugin):

    def load(self):
        self.giveaways_left = defaultdict(lambda: 3)
        self.in_progress = dict()

        context = dict(
            plugin = self,
            bot    = self.bot
        )
        self.add_web_handlers(
            (r'/giveaways/user', GiveawayInfo, context),
            (r'/giveaways/start', GiveawayStart, context)
        )

    def start_giveaway(self, giveaway):
        # Only one giveaway at a time
        if giveaway.server.id in self.in_progress:
            return False
        # Check user limit
        if self.giveaways_left_for(giveaway.user) <= 0:
            return False
        # Consume one token
        self.giveaways_left[giveaway.user.id] -= 1
        # Lock server
        self.in_progress[giveaway.server.id] = set()
        # Runs the giveaway
        self.run_async(self.manage_giveaway(giveaway))
        return True

    @command(p.string('!enter'))
    async def enter_giveaway(self, message):
        try:
            giveaway = self.in_progress[message.server.id]
        except KeyError:
            return
        else:
            giveaway.add(message.author)

    def giveaways_left_for(self, user):
        return self.giveaways_left[user.id]

    def giveaway_message_content(self, giveaway, timeout):
        registered = self.in_progress[giveaway.server.id]

        data = dict(
            user = giveaway.user.mention,
            title = giveaway.title,
            count = len(registered),
            registered = ' '.join([user.mention for user in registered]),
            time_left = timeout
        )
        return (
            '{user} started a giveaway: `{title}`\n'
            'Type `!enter` to participate\n'
            '{count} users are currently registered: {registered}\n'
            'The giveaway will end in approximately {time_left} seconds'
                .format(**data)
        )


    async def manage_giveaway(self, giveaway):
        timeout = min(giveaway.timeout, c.MAX_GIVEAWAY_TIME)
        sleep_duration = 5
        last_registered_count = 0

        send_notification = lambda: self.send_message(
            giveaway.server.default_channel,
            self.giveaway_message_content(giveaway, timeout)
        )

        message = await send_notification()

        while timeout > 0:

            await asyncio.sleep(sleep_duration)
            timeout -= sleep_duration

            registered_count = len(self.in_progress[giveaway.server.id])
            if registered_count > last_registered_count:
                last_registered_count = registered_count
                await self.bot.delete_message(message)
                message = await send_notification()
            else:
                await self.edit_message(
                    message,
                    self.giveaway_message_content(giveaway, timeout)
                )

        await self.bot.delete_message(message)
        await self.end_giveaway(giveaway)

    async def end_giveaway(self, giveaway):
        registered = self.in_progress[giveaway.server.id]
        del self.in_progress[giveaway.server.id]

        if len(registered) == 0:
            await self.send_message(
                giveaway.server.default_channel,
                'No one registered for the giveaway 😢\nNo one wins'
            )
        else:
            winner = choice(list(registered))
            await self.send_message(
                giveaway.server.default_channel,
                '{} You are the giveaway winner!\n'
                'I will whisper you your prize shortly'
                    .format(winner.mention)
            )
            await self.send_message(
                winner,
                'You won the giveaway of {} on `{}`\n'
                'Here is your prize:\n'
                '{}'
                    .format(
                        giveaway.user.mention,
                        giveaway.server.name,
                        f.code_block(giveaway.content)
                    )
            )
