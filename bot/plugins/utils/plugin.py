from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import master_only

from .units import unit_value_parser, system_convert, sum_units
from .timezones import time_parser, Time, TIMEZONES

from itertools import groupby

import json

TZ_INFOS_FILE = '/tmp/globibot/tzs'

class Utils(Plugin):

    def load(self):
        self.last_time = None

        try:
            with open(TZ_INFOS_FILE, 'r') as f:
                self.tzs = json.load(f)
        except:
            self.tzs = dict()

        self.last_values_to_convert = dict()

    def dump_tzs(self):
        with open(TZ_INFOS_FILE, 'w') as f:
            json.dump(self.tzs, f)

    PREFIXES = ['!', '-', '/']

    prefixed = lambda s: p.one_of(p.string, *[
        '{}{}'.format(prefix, s)
        for prefix in Utils.PREFIXES
    ]).named('[{}]{}'.format(''.join(Utils.PREFIXES), s)) >> p.to_s

    @command(p.bind(p.oneplus(p.sparsed(unit_value_parser)), 'unit_values'))
    async def store_unit_values(self, message, unit_values):
        self.last_values_to_convert[message.channel.id] = (unit_values, self.unit_convert)

    # @command(p.bind(p.oneplus(p.sparsed(time_parser)), 'times'))
    # async def store_time_values(self, message, times):
    #     self.last_values_to_convert[message.channel.id] = (times, self.time_convert)

    @command(p.string('!convert') + p.eof)
    async def convert_last(self, message):
        try:
            values, convertor = self.last_values_to_convert[message.channel.id]
        except KeyError:
            pass
        else:
            await convertor(message, values)

    @command(p.string('!convert') + p.bind(p.oneplus(p.sparsed(unit_value_parser)), 'unit_values'))
    async def unit_convert(self, message, unit_values):
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

    @command(p.string('!tz') + p.string('set') + p.bind(p.word, 'tz'))
    async def set_tz(self, message, tz):
        tz = tz.upper()

        if tz not in TIMEZONES:
            await self.send_message(
                message.channel,
                '{} available timezones are `{}`'.format(message.author.mention, TIMEZONES),
                delete_after=15
            )
            return

        self.tzs[message.author.id] = tz
        self.dump_tzs()

        await self.send_message(
            message.channel,
            '{} I set your default timezone to `{}`'.format(message.author.mention, tz),
            delete_after=5
        )

    # @command(p.string('!convert') + p.bind(p.oneplus(p.sparsed(time_parser)), 'times'))
    # async def time_convert(self, message, times):
    #     tz = self.tzs.get(message.author.id)
    #     valid_time_props = [time for time in times if any(map(lambda x: x is not None, time[1:]))]

    #     if not valid_time_props:
    #         return

    #     times = [Time(h, m, mer, r_tz or tz) for (h, m, mer, r_tz) in valid_time_props]
    #     response = f.code_block('\n'.join(
    #         '{}'.format(t) for t in times
    #     ))

    #     self.last_time = times[-1]

    #     await self.send_message(
    #         message.channel,
    #         response,
    #         delete_after=10
    #     )

    # @command(p.string('!timetable') + p.bind(p.maybe(time_parser), 'time_prop'))
    # async def timetable(self, message, time_prop=None):
    #     if time_prop is not None and not any(time_prop[1:]):
    #         return

    #     time = Time(*time_prop) if time_prop else self.last_time
    #     if time_prop and time_prop[3] is None:
    #         time.tz = self.tzs.get(message.author.id)

    #     await self.send_message(
    #         message.channel,
    #         f.code_block(time.timetable()),
    #         delete_after=30
    #     )

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

        m = await self.send_message(message.channel, 'processing...')

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

        await self.bot.delete_message(m)
