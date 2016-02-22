from discord import Client as DiscordClient
from discord import ChannelType

from utils.logging import logger

import asyncio

class Globibot(DiscordClient):

    def __init__(self, web, module_classes, *credentials):
        super().__init__()

        self.web = web

        logger.debug('Initializing modules...')
        self.modules = [cls(self) for cls in module_classes]

        self.credentials = credentials

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
