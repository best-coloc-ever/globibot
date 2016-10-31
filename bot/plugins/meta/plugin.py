from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command
from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import master_only

from functools import reduce

from .permissions import permission_names, PERMISSION_NAMES

from discord import ChannelType, Game

class Meta(Plugin):

    @command(
        p.string('!permissions') + p.bind(p.maybe(p.channel), 'channel_id'),
        master_only
    )
    async def permissions(self, message, channel_id=None):
        if channel_id is None:
            channel_id = message.channel.id

        channel = next(
            channel for channel in message.server.channels
            if channel.id == str(channel_id)
        )

        perms = [' - {}'.format(perm) for perm in self.permissions_in(channel)]

        await self.send_message(
            message.channel,
            'In {}, I can:\n{}'
                .format(f.channel(channel_id), f.code_block(perms)),
            delete_after = 30
        )

    @command(p.string('!channels'))
    async def channels(self, message):
        channels = [
            (channel.name, channel.id)
            for channel in message.server.channels
        ]

        await self.send_message(
            message.channel,
            f.code_block(f.format_sql_rows(channels)),
            delete_after = 30
        )

    @command(
        p.string('!where-can-you') + p.bind(p.word, 'what'), master_only
    )
    async def where_can_you(self, message, what):
        perm_name = PERMISSION_NAMES[what]
        permissions = [
            (channel, self.permissions_in(channel))
            for channel in message.server.channels
        ]

        where = [
            channel.id for channel, perms in permissions
            if perm_name in perms and channel.type == ChannelType.text
        ]

        await self.send_message(
            message.channel,
            'On this server, I can `{}` {}'
                .format(
                    PERMISSION_NAMES[what],
                    ('in ' + ' '.join(map(f.channel, where))) if where else '`nowhere`'
                ),
            delete_after = 30
        )

    @command(p.string('!status'), master_only)
    async def status(self, message):
        status = message.clean_content[len('!status'):].strip()
        await self.bot.change_status(Game(name=status))

    @command(p.string('!name'), master_only)
    async def name(self, message):
        name = message.clean_content[len('!name'):].strip()
        await self.bot.edit_profile(username=name)

    def permissions_in(self, channel):
        member = channel.server.get_member(self.bot.user.id)

        standard_perms = channel.permissions_for(member)
        overwrites = [channel.overwrites_for(role) for role in member.roles]

        sets = [permission_names(perms) for perms in [standard_perms] + overwrites]

        return reduce(set.union, sets)
