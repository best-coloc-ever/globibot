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

        self.last_message = None

    async def dispatch(self, message):
        self.last_message = message

        for format, command in self.actions:
            parsed = parse(format, message.content)
            if parsed:
                await command(self, message, **parsed.named)

    async def respond(self, content):
        await self.bot.client.send_message(self.last_message.channel, content)

    async def respond_file(self, file_path):
        await self.bot.client.send_file(self.last_message.channel, file_path)

    def _action_list(self):
        actions = []

        for _, function in getmembers(self.__class__, isfunction):
            if hasattr(function, Module.FORMAT_MAGIC_ATTR):
                formats = getattr(function, Module.FORMAT_MAGIC_ATTR)
                for format in formats:
                    action = (format, function)
                    actions.append(action)

        return actions

def command(format):

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
