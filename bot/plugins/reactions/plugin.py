from globibot.lib.plugin import Plugin

from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers.hooks import master_only

import re

URL_PATTERN = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

class Reactions(Plugin):

    async def on_new(self, message):
        if URL_PATTERN.findall(message.content) or message.attachments:
            await self.bot.add_reaction(message, '👍')
            await self.bot.add_reaction(message, '👎')

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
                            return
                        except:
                            break

            await self.send_message(message.channel, "I can't use that emoji 😢", delete_after=5)
            await self.bot.add_reaction(last_message, '❓')
