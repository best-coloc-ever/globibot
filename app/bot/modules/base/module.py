from .command import FORMAT_MAGIC_ATTR
from .logging import logger
from .errors import ModuleException, unexpected_error_str, unexpected_async_error_str

from traceback import format_exc
from functools import partial
from inspect import getmembers, isfunction
from parse import parse

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
        for format, command in self.actions:
            parsed = parse(format, message.content)
            if parsed:
                future = self.invoke_command(command, message, **parsed.named)
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

        message = await self.bot.send_file(channel, file_path)
        self.process_message(message, clear)
        return message

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
            if hasattr(function, FORMAT_MAGIC_ATTR):
                formats = getattr(function, FORMAT_MAGIC_ATTR)
                for format in formats:
                    action = (format, function)
                    actions.append(action)

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
