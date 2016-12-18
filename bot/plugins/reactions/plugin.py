from globibot.lib.plugin import Plugin

from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers.hooks import master_only

import re

URL_PATTERN = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

class Reactions(Plugin):

    def load(self):
        self.votes = dict()

    async def on_new(self, message):
        if URL_PATTERN.findall(message.content) or message.attachments:
            await self.bot.add_reaction(message, '👍')
            await self.bot.add_reaction(message, '👎')

    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == '❌':
            await self.check_vote_delete(reaction)
        elif reaction.emoji == '👎':
            await self.check_downvote(reaction)

    @command(p.string('!react') + p.bind(p.mention, 'who') + p.bind(p.word, 'emoji'), master_only)
    async def react_last_user(self, message, who, emoji):
        try:
            last_message = next(
                msg for msg in list(self.bot.messages)[-2::-1]
                if msg.channel.id == message.channel.id and msg.author.id == str(who)
            )
        except StopIteration:
            self.debug('No Message')
        else:
            await self.bot.add_reaction(last_message, emoji)
            await self.bot.delete_message(message)

    @command(p.string('!react') + p.bind(p.mention, 'who') + p.bind(p.emoji, 'emoji_id'), master_only)
    async def react_last_user_emoji(self, message, who, emoji_id):
        try:
            last_message = next(
                msg for msg in list(self.bot.messages)[-2::-1]
                if msg.channel.id == message.channel.id and msg.author.id == str(who)
            )
        except StopIteration:
            self.debug('No Message')
        else:
            for server in self.bot.servers:
                for emoji in server.emojis:
                    if emoji.id == str(emoji_id):
                        try:
                            await self.bot.add_reaction(last_message, emoji)
                            await self.bot.delete_message(message)
                            return
                        except:
                            break

            await self.send_message(message.channel, "I can't use that emoji 😢", delete_after=5)
            await self.bot.add_reaction(last_message, '❓')

    @command(
        p.string('!votedel') + p.bind(p.mention, 'who') +
        p.bind(p.maybe(p.integer), 'count'),
        master_only
    )
    async def votedel(self, message, who, count=10):
        try:
            last_message = next(
                msg for msg in list(self.bot.messages)[-2::-1]
                if msg.channel.id == message.channel.id and msg.author.id == str(who)
            )
        except StopIteration:
            self.debug('No Message')
        else:
            self.votes[last_message.id] = (last_message, count)
            await self.bot.add_reaction(last_message, '❌')
            await self.send_message(
                message.channel,
                'Deletion vote started: Cast your vote by clicking the ❌ reaction in order to delete {}\'s message ({} votes needed)'
                    .format(last_message.author.mention, count),
                delete_after = 10
            )

    async def check_vote_delete(self, reaction):
        try:
            message, count = self.votes[reaction.message.id]
        except KeyError:
            pass
        else:
            if reaction.count >= count:
                del self.votes[reaction.message.id]

                await self.bot.delete_message(message)
                await self.send_message(
                    reaction.message.channel,
                    'Deletion vote passed',
                    delete_after = 5
                )

    async def check_downvote(self, reaction):
        if reaction.count >= 10:
            await self.bot.delete_message(reaction.message)
            await self.send_message(
                reaction.message.channel,
                '{}, I deleted your post since it was disliked too many times'
                    .format(reaction.message.author.mention),
                delete_after = 10
            )
