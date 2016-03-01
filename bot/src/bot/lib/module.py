from .decorators.validator import COMMAND_VALIDATORS_ATTR
from .logging import logger
from .discord import EMOTES
from .errors import ModuleException, unexpected_error_str, unexpected_async_error_str

from discord.errors import Forbidden
from traceback import format_exc
from functools import partial
from inspect import getmembers, isfunction

import logging
import asyncio

class Module:

    def __init__(self, bot):
        self.bot = bot
        self.actions = self._action_list()

        # Logging helpers
        self.debug    = partial(self.log, logging.DEBUG)
        self.info     = partial(self.log, logging.INFO)
        self.warning  = partial(self.log, logging.WARNING)
        self.error    = partial(self.log, logging.ERROR)
        self.critical = partial(self.log, logging.CRITICAL)

    async def dispatch(self, message):
        for validator, action in self.actions:
            is_match, context = validator(message.content)
            if is_match:
                future = self.invoke_command(action, message, **context)
                asyncio.ensure_future(future)

        self.on_message(message)

    def on_message(self, message):
        pass

    async def send_message(self, channel, content, clear=0):
        self.debug('Sending message: "{}"'.format(content))

        try:
            message = await self.bot.send_message(channel, content)
            self.process_message(message, clear)
            return message
        except Exception as e:
            self.error('Failed to send message: {}'.format(e))

    async def send_file(self, channel, file_path, clear=0):
        self.debug('Sending file: "{}"'.format(file_path))

        try:
            message = await self.bot.send_file(channel, file_path)
            self.process_message(message, clear)
            return message
        except Forbidden:
            await self.send_message(
                channel,
                (
                    'I don\'t seem to have permission to upload '
                    'files in this channel {}'
                ).format(
                    EMOTES.LirikFeels
                )
            )
        except Exception as e:
            self.error('Failed to upload file: {}'.format(e))

    def process_message(self, message, clear):
        if clear > 0:
            future = self.delete_message(message, clear)
            asyncio.ensure_future(future)

    async def delete_message(self, message, after):
        await asyncio.sleep(after)
        await self.bot.delete_message(message)

    async def invoke_command(self, command, message, **context):
        try:
            await command(self, message, **context)
        except ModuleException as me:
            await self.send_message(
                message.channel,
                me.error(message)
            )
        except Exception:
            error_str = unexpected_error_str(message, format_exc(10))
            await self.send_message(message.channel, error_str)

    def log(self, level, message):
        extra = {
            'module_name': self.__class__.__name__
        }
        logger.log(level, message, extra=extra)

    def _action_list(self):
        actions = []

        for _, function in getmembers(self.__class__, isfunction):
            if hasattr(function, COMMAND_VALIDATORS_ATTR):
                validators = getattr(function, COMMAND_VALIDATORS_ATTR)
                for validator in validators:
                    actions.append((validator, function))

        return actions

    def run_async(self, future, report_channel):

        async def run():
            try:
                await future
            except Exception:
                error_str = unexpected_async_error_str(format_exc(10))
                if report_channel:
                    await self.send_message(report_channel, error_str)
                else:
                    self.error(error_str)

        asyncio.ensure_future(run())
