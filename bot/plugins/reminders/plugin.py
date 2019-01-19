from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import global_cooldown

from collections import namedtuple, defaultdict
from datetime import datetime, timedelta

import asyncio
import json

REMINDERS_FILE = '/tmp/globibot/reminders.json'

Reminder = namedtuple('Reminder', [
    'author_id',
    'server_id',
    'channel_id',
    'timestamp',
    'topic'
])

DELTA_NAME = {
    's': 'seconds',
    'm': 'minutes',
    'h': 'hours',
    'd': 'days',
}

RawDelta = namedtuple('RawDelta', ['val', 'unit'])

def to_time_delta(raw_deltas):
    print(raw_deltas)
    deltas = defaultdict(int)
    for raw_delta in raw_deltas:
        deltas[DELTA_NAME[raw_delta.unit]] += raw_delta.val
    return timedelta(**deltas)

def to_raw_delta(parsed):
    raw_val, unit = parsed
    return RawDelta(int(raw_val), unit)

delta_types = { 's', 'm', 'h', 'd' }
delta_type_grammar = p.one_of(p.string, *delta_types)
raw_delta_parser = (
    p.integer +
    (delta_type_grammar >> p.to_s)
).named('XX s/m/h/d') >> to_raw_delta
delta_parser = p.oneplus(raw_delta_parser) >> to_time_delta

def format_reminder(reminder):
    seconds = reminder.timestamp - datetime.now().timestamp()
    delta = timedelta(seconds=seconds)
    return f'{str(delta): <15} => {reminder.topic}'

class ReminderList(list):

    def __init__(self):
        super().__init__()
        self.load_reminders()

    def load_reminders(self):
        try:
            with open(REMINDERS_FILE, 'r') as f:
                self.extend([Reminder(*data) for data in json.load(f)])
        except:
            pass

    def save_reminders(self):
        with open(REMINDERS_FILE, 'w') as f:
            json.dump(self, f)

    def add(self, reminder):
        self.append(reminder)
        self.save_reminders()

    def rm(self, reminder):
        self.remove(reminder)
        self.save_reminders()

class Reminders(Plugin):

    def load(self):
        self.reminders = ReminderList()
        self.debug(self.reminders)
        for reminder in self.reminders:
            self.run_async(self.queue_reminder(reminder))

    def add_reminder(self, message, stamp, topic):
        reminder = Reminder(
            message.author.id,
            message.server.id if message.server else None,
            message.channel.id,
            stamp,
            topic
        )

        self.reminders.add(reminder)

        self.run_async(self.queue_reminder(reminder))

    async def queue_reminder(self, reminder):
        timeout = reminder.timestamp - datetime.now().timestamp()
        await asyncio.sleep(timeout)
        if reminder in self.reminders:
            self.reminders.rm(reminder)
            await self.remind(reminder)

    async def remind(self, reminder):
        if reminder.server_id is None:
            destination = self.bot.find_user(reminder.author_id)
        else:
            server = self.bot.find_server(reminder.server_id)
            destination = next(
                ch for ch in server.channels
                if ch.id == reminder.channel_id
            )
        await self.send_message(
            destination,
            f'<@{reminder.author_id}> Time is up!\n'
            f'You wanted to be reminded of: `{reminder.topic}`'
        )

    @command(
            p.string('!remindme')
        +   p.oneplus(p.some_type(p.TokenType.Space))
        +   p.bind(delta_parser, 'delta')
        +   p.oneplus(p.some_type(p.TokenType.Space))
        +   p.bind(p.many(p.any_type >> p.to_s), 'raw_topic'),
        ignored_tokens = ()
    )
    async def remindme(self, message, delta, raw_topic):
        topic = ''.join(raw_topic)
        stamp = (datetime.now() + delta).timestamp()

        self.add_reminder(message, stamp, topic)

        await self.send_message(
            message.channel,
            f'{message.author.mention} I will remind you of `{topic}` in {delta}',
            delete_after=5
        )

    @command(
            p.string('!reminders')
        +   p.eof
    )
    async def list_reminders(self, message):
        reminders = [
            reminder for reminder in self.reminders
            if reminder.author_id == message.author.id
        ]
        if not reminders:
            answer = 'You have no current alarms'
        else:
            pretty_reminders = f.code_block('\n'.join(
                f'[{i}] {format_reminder(reminder)}'
                for i, reminder in enumerate(reminders)
            ))
            answer = f'You have {len(reminders)} current alarms: {pretty_reminders}'
        await self.send_message(
            message.channel,
            f'{message.author.mention} {answer}',
            delete_after=10
        )

    @command(
            p.string('!reminders')
        +   p.string('remove')
        +   p.bind(p.integer, 'reminder_id')
    )
    async def remove_reminder(self, message, reminder_id):
        reminders = [
            reminder for reminder in self.reminders
            if reminder.author_id == message.author.id
        ]
        try:
            reminder = reminders[reminder_id]
        except IndexError:
            answer = 'No such reminder'
        else:
            self.reminders.remove(reminder)
            answer = 'I removed the alarm'
        await self.send_message(
            message.channel,
            f'{message.author.mention} {answer}',
            delete_after=5
        )

