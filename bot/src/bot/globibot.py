from discord import Client as DiscordClient
from discord import ChannelType

from utils.logging import logger

from .modules import module_class_by_name
from . import constants as c

import asyncio
import sys

class Globibot(DiscordClient):

    def __init__(self, config, web):
        super().__init__()

        self.config = config
        self.web = web

        self.credentials = self.load_credentials()
        self.modules = self.load_modules()

        self.masters = [str(id) for id in self.config.get(c.MASTER_IDS_KEY, [])]

    def load_credentials(self):
        email = self.config.get(c.GLOBIBOT_EMAIL_KEY)
        password = self.config.get(c.GLOBIBOT_PASSWORD_KEY)

        if email is None or password is None:
            sys.exit('Missing credentials in: "{}"'.format(c.CONFIG_FILE))

        return (email, password)

    def load_modules(self):
        enabled_modules = self.config.get(c.ENABLED_MODULES_KEY)

        if enabled_modules is None:
            enabled_modules = {}

        module_specs = [
            (cls, config) for cls, config in [
                (module_class_by_name(name), config)
                for name, config in enabled_modules.items()
            ]
            if cls is not None
        ]

        logger.debug('Initializing {} modules...'.format(len(module_specs)))
        modules = [cls(self, spec) for cls, spec in module_specs]
        logger.debug('Done')

        return modules
    async def boot(self):
        await self.start(*self.credentials)

    async def shutdown(self):
        await self.logout()

    async def on_ready(self):
        logger.info('Globibot is online')
        logger.info('Operating on {} discord servers'.format(len(self.servers)))

    async def on_message(self, message):
        if message.author.id != self.user.id: # ignoring our own messages
            logger.debug('Dispatching message "{}"'.format(message.content))

            for module in self.modules:
                future = module.dispatch(message)
                asyncio.ensure_future(future)

    async def on_error(self, event, *args, **kwargs):
        logger.error('Got a client error: {} {} {}'.format(event, args, kwargs))

    def find_voice_channel(self, name, server):
        is_matching_channel = lambda channel: \
            channel.type == ChannelType.voice and \
            channel.name.lower() == name.lower()

        matching_channels = filter(is_matching_channel, server.channels)
        return next(matching_channels, None) # Returning first match or None
