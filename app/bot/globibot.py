from discord import Client as DiscordClient

from utils.logging import logger

class Globibot:

    def __init__(self, modules, *credentials):
        self.modules = modules
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
        logger.info('Detected {} discord servers'.format(self.client.servers))
