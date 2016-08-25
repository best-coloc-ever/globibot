from bot.lib.plugin import Plugin
from bot.lib.decorators import command

from bot.lib.helpers import parsing as p
from bot.lib.helpers import formatting as f
from bot.lib.helpers.hooks import master_only

from .units import unit_value_parser, system_convert, sum_units

from itertools import groupby

class Utils(Plugin):

    PREFIXES = ['!', '-', '/']

    prefixed = lambda s: p.one_of(p.string, *[
        '{}{}'.format(prefix, s)
        for prefix in Utils.PREFIXES
    ]).named('[{}]{}'.format(''.join(Utils.PREFIXES), s)) >> p.to_s

    @command(p.bind(p.oneplus(p.sparsed(unit_value_parser)), 'unit_values'))
    async def convert(self, message, unit_values):
        converted = [(uv, system_convert(uv)) for uv in unit_values]
        output = ['{} = {}'.format(uv, conv) for uv, conv in converted]

        for t, uvs in groupby(converted, key=lambda uvs: type(uvs[0].unit)):
            values = list(map(lambda x: x[0], uvs))

            if len(values) >= 2:
                summed = sum_units(*values)
                converted_summed = system_convert(summed)
                output.append(
                    '{} total: {} = {}'
                        .format(t.__name__.lower(), summed, converted_summed)
                )

        await self.send_message(
            message.channel,
            'Converted units\n{}'
                .format(f.code_block(output)),
            delete_after = 60
        )

    @command(p.string('!user') + p.bind(p.mention, 'user'))
    async def user_id(self, message, user):
        await self.send_message(
            message.channel,
            '{}'.format(user),
            delete_after=15
        )

    @command(
        p.string('!master') + p.string('add') + p.bind(p.mention, 'user'),
        master_only
    )
    async def add_master(self, message, user):
        self.bot.masters.append(str(user))

        await self.send_message(
            message.channel,
            '{} can now use master commands'.format(f.mention(user)),
            delete_after=20
        )

    @command(p.string('!master') + p.string('remove') + p.bind(p.mention, 'user'))
    async def remove_master(self, message, user):
        if message.author.id != '89108411861467136':
            return

        self.bot.masters.remove(str(user))

        await self.send_message(
            message.channel,
            '{} can no longer use master commands'.format(f.mention(user)),
            delete_after=20
        )

    @command(p.string('!user') + p.bind(p.integer, 'user_id'))
    async def user(self, message, user_id):
        await self.send_message(
            message.channel,
            f.mention(user_id),
            delete_after=15
        )

    @command(p.string('!channel') + p.bind(p.channel, 'channel'))
    async def channel_id(self, message, channel):
        await self.send_message(
            message.channel,
            '{}'.format(channel),
            delete_after=15
        )

    @command(p.string('!channel') + p.bind(p.integer, 'channel_id'))
    async def channel(self, message, channel_id):
        await self.send_message(
            message.channel,
            f.channel(channel_id),
            delete_after=15
        )

    @command(p.string('!server') + p.eof)
    async def server_id(self, message):
        await self.send_message(
            message.channel,
            '{}'.format(message.server.id),
            delete_after=15
        )

    @command(
        p.string('!block') + p.bind(p.mention, 'who'),
        master_only
    )
    async def block(self, message, who):
        # TODO: Actually block that bitch 😂
        await self.send_message(
            message.channel,
            '{} is now blocked 👍'.format(f.mention(who))
        )

    @command(
        p.string('!unsafe') + p.bind(p.snippet, 'snippet'),
        master_only
    )
    async def sql_exec(self, message, snippet):
        if snippet.language.lower() != 'sql':
            return

        try:
            with self.transaction() as trans:
                trans.execute(snippet.code)
                rows = trans.fetchall()
                self.debug(rows)
                if rows:
                    text = f.code_block(f.format_sql_rows(rows))
                else:
                    text = 'Request executed successfully\n`no output`'
                await self.send_message(message.channel, text)
        except Exception as e:
            await self.send_message(message.channel, '```\n{}\n```'.format(e))
