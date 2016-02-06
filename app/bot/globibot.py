from discord import Client as DiscordClient

from utils.logging import logger

import asyncio

class Globibot:

    def __init__(self, web_app, module_classes, *credentials):
        self.web_app = web_app
        self.modules = list(map(lambda cls: cls(self), module_classes))
        self.credentials = credentials

        self.client = DiscordClient()
        self.client.on_ready = self.on_ready
        self.client.on_message = self.on_message

    async def boot(self):
        await self.client.start(*self.credentials)

    async def shutdown(self):
        await self.client.logout()

    async def on_ready(self):
        logger.info('Globibot is online')
        logger.info('Detected {} discord servers'.format(len(self.client.servers)))

    async def on_message(self, message):
        for module in self.modules:
            future = module.dispatch(message)
            asyncio.ensure_future(future)
