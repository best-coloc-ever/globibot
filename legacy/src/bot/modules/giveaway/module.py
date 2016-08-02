from bot.lib.module import Module
from bot.lib.decorators import simple_command
from bot.lib.discord import EMOTES

from . import errors

from collections import defaultdict
from time import time

import asyncio
import random

class Giveaway(Module):

    GIVEAWAY_TIME = 90 # seconds

    class Item:

        def __init__(self, content=None, description=None):
            self.content = content
            self.description = description

        def __str__(self):
            return (
                '`{description}`\n'
                '```\n'
                '{content}\n'
                '```'
            ).format(
                description=self.description if self.description else 'No description',
                content=self.content
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.items = defaultdict(Giveaway.Item)

        self.giveaway_channel = None
        self.giveaway_author = None
        self.giveaway_start = None
        self.participants = set()

    @simple_command('!giveaway')
    async def current_giveaway(self, message):
        if not message.channel.is_private:
            raise errors.NotPrivateChannel

        if message.author.id in self.items:
            await self.send_message(
                message.channel,
                (
                    'Your current giveaway is:\n'
                    '{}\n'
                    'Use `!giveaway start` in a channel to start your giveaway'
                ).format(
                    self.items[message.author.id]
                )
            )
        else:
            raise errors.NoCurrentGiveaway

    @simple_command('!giveaway content {content}')
    async def set_giveaway_content(self, message, content):
        if not message.channel.is_private:
            raise errors.NotPrivateChannel

        already_had_giveaway = message.author.id in self.items
        self.items[message.author.id].content = content
        if already_had_giveaway:
            await self.send_message(
                message.channel,
                (
                    'You set your giveaway content to `{}`\n'
                    'Use `!giveaway start` in a channel to start your giveaway'
                ).format(content)
            )
        else:
            await self.send_message(
                message.channel,
                (
                    'I successfully registered your giveaway of `{}`\n'
                    'You can add a description with '
                    '`!giveaway description *your description*`\n'
                    'Use `!giveaway start` in a channel to start your giveaway'
                ).format(
                    content
                )
            )

    @simple_command('!giveaway description {description}')
    async def set_giveaway_description(self, message, description):
        if not message.channel.is_private:
            raise errors.NotPrivateChannel

        already_had_giveaway = message.author.id in self.items
        self.items[message.author.id].description = description
        if already_had_giveaway:
            await self.send_message(
                message.channel,
                'You set your giveaway description to `{}`'.format(description)
            )
        else:
            await self.send_message(
                message.channel,
                (
                    'I set the description of your next giveaway to `{}`\n'
                    'You must now add a content with '
                    '`!giveaway content *your content*`\n'
                ).format(
                    description
                )
            )

    @simple_command('!giveaway start')
    async def start_giveaway(self, message):
        if self.giveaway_channel:
            raise errors.AlreadyInProgress

        if message.channel.is_private:
            raise errors.NotPublicChannel

        if message.author.id not in self.items:
            raise errors.IncorrectGiveaway

        item = self.items[message.author.id]
        if item.content is None:
            raise errors.IncorrectGiveaway

        self.giveaway_channel = message.channel
        self.giveaway_author = message.author
        self.giveaway_start = time()
        del self.items[message.author.id]

        self.run_async(
            self.run_giveaway(message.channel, message.author, item),
            message.channel
        )

    @simple_command('!giveaway join')
    async def join_giveaway(self, message):
        if self.giveaway_channel != message.channel:
            return

        if message.author == self.giveaway_author:
            raise errors.CantJoinYourOwnGiveaway

        self.participants.add(message.author)

        await self.send_message(
            message.channel,
            (
                '**{}** participants have joined the giveaway so far!\n'
                '`{} seconds` left to join with `!giveaway join`!'
            ).format(
                len(self.participants),
                int(Giveaway.GIVEAWAY_TIME - (time() - self.giveaway_start))
            ),
            15
        )

    async def run_giveaway(self, channel, who, item):
        await self.send_message(
            channel,
            (
                '{} wants to giveaway `{}`\n'
                'Type `!giveaway join` to participate to the giveaway!\n'
                'The winner will be chosen randomly in {} seconds'
            ).format(
                who.mention,
                item.description if item.description else 'No description',
                Giveaway.GIVEAWAY_TIME
            )
        )

        await asyncio.sleep(Giveaway.GIVEAWAY_TIME)

        self.giveaway_channel = None
        self.giveaway_author = None

        if not self.participants:
            await self.send_message(
                channel,
                'No one registered for the giveaway {}'.format(EMOTES.LirikFeels)
            )
            return

        winner = random.choice(list(self.participants))
        count = len(self.participants)
        self.participants.clear()

        await self.send_message(
            winner,
            (
                'Congratulations! You won {}\n'
                'Don\'t forget to thank {} {}'
            ).format(
                item,
                who.mention,
                EMOTES.LirikH
            )
        )

        await self.send_message(
            channel,
            (
                'Congratulations to {} for winning the giveaway (1 in {} chance)!\n'
                'Thank you {} for your generosity {}'
            ).format(
                winner.mention,
                count,
                who.mention,
                EMOTES.LirikH
            )
        )
