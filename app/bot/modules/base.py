from inspect import getmembers, isfunction

from parse import parse

from .logging import logger
import logging

import asyncio

class Module:

    FORMAT_MAGIC_ATTR = 'command_formats'

    def __init__(self, bot):
        self.bot = bot
        self.actions = self._action_list()

    async def dispatch(self, message):
        for format, command in self.actions:
            parsed = parse(format, message.content)
            if parsed:
                future = command(self, message, **parsed.named)
                asyncio.ensure_future(future)

    def _action_list(self):
        actions = []

        for _, function in getmembers(self.__class__, isfunction):
            if hasattr(function, Module.FORMAT_MAGIC_ATTR):
                formats = getattr(function, Module.FORMAT_MAGIC_ATTR)
                for format in formats:
                    action = (format, function)
                    actions.append(action)

        return actions

    async def send_message(self, channel, content):
        self.debug('Sending message: "{}"'.format(content))

        await self.bot.send_message(channel, content)

    async def send_file(self, channel, file_path):
        self.debug('Sending file: "{}"'.format(file_path))

        await self.bot.send_file(channel, file_path)

    def log(self, level, message):
        extra = {
            'module_name': self.__class__.__name__
        }
        logger.log(level, message, extra=extra)

    def debug(self, message):
        self.log(logging.DEBUG, message)

    def info(self, message):
        self.log(logging.INFO, message)

    def warning(self, message):
        self.log(logging.WARNING, message)

    def error(self, message):
        self.log(logging.ERROR, message)

    def critical(self, message):
        self.log(logging.CRITICAL, message)


def command(format):
    '''Intended to be used as a decorator
    Will add some metadata to the decorated function to hint the Module class to
    handle it as an action
    '''
    def wrapped(func):

        def call(*args, **kwargs):
            return func(*args, **kwargs)

        if hasattr(func, Module.FORMAT_MAGIC_ATTR):
            formats = getattr(func, Module.FORMAT_MAGIC_ATTR)
            formats.append(format)
            setattr(call, Module.FORMAT_MAGIC_ATTR, formats)
        else:
            setattr(call, Module.FORMAT_MAGIC_ATTR, [format])
        return call

    return wrapped
