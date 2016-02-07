from discord import Client as DiscordClient

from utils.logging import logger

import asyncio

class Globibot(DiscordClient):

    def __init__(self, web, module_classes, *credentials):
        super().__init__()

        self.web_app = web_app
        self.modules = list(map(lambda cls: cls(self), module_classes))
        self.credentials = credentials


    async def boot(self):
        await self.start(*self.credentials)

    async def shutdown(self):
        await self.logout()

    async def on_ready(self):
        logger.info('Globibot is online')
        logger.info('Operating on {} discord servers'.format(len(self.servers)))

    async def on_message(self, message):
        for module in self.modules:
            future = module.dispatch(message)
            asyncio.ensure_future(future)
