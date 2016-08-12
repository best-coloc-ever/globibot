from asyncio import ensure_future
from discord import Client as DiscordClient
from psycopg2 import connect as db_connect

from utils.logging import logger

from .lib.plugin import Plugin
from .lib.plugin_collection import PluginCollection

from . import constants as c

class Globibot(DiscordClient):

    def __init__(self, config, db_config, web):
        super().__init__()

        self.db = db_connect(
            host = db_config.get(c.DB_HOST_KEY),
            user = db_config.get(c.DB_USER_KEY)
        )

        self.config = config
        self.web = web
        self.plugin_collection = PluginCollection(self, self.plugin_descriptors)

        self.token = self.config.get(c.GLOBIBOT_TOKEN_KEY)

        self.masters = [
            str(id) for id in
            self.config.get(c.MASTER_IDS_KEY, [])
        ]

        self.enabled_servers = self.config.get(c.ENABLED_SERVERS_KEY, [])

    '''
    Events
    '''

    async def on_ready(self):
        logger.info(
            'Globibot ({}) is online'
                .format(self.user.id)
        )

        self.plugin_collection.load_plugins()

    async def on_message(self, message):
        self.debug_message(message, 'received')
        self._dispatch_message(Plugin.dispatch_new, message)

    async def on_message_delete(self, message):
        self.debug_message(message, 'deleted')
        self._dispatch_message(Plugin.dispatch_deleted, message)

    async def on_message_edit(self, before, after):
        self.debug_message(after, 'edited')
        self._dispatch_message(Plugin.dispatch_edit, before, after)

    async def on_channel_create(self, channel):
        logger.debug(
            'The "{}" channel has been created on the server "{}"'
                .format(channel.name, channel.server.name)
        )

    async def on_channel_delete(self, channel):
        logger.debug(
            'The "{}" channel has been removed on the server "{}"'
                .format(channel.name, channel.server.name)
        )

    async def on_channel_update(self, before, after):
        logger.debug(
            'The "{}" channel has been modified on the server "{}"'
                .format(before.name, before.server.name)
        )

    async def on_member_join(self, member):
        logger.debug(
            '{} ({}) has joined the server "{}"'
                .format(member.name, member.id, member.server.name)
        )

    async def on_member_remove(self, member):
        logger.debug(
            '{} ({}) has left the server "{}"'
                .format(member.name, member.id, member.server.name)
        )

    async def on_member_update(self, before, after):
        self._dispatch(Plugin.dispatch_member_update, before, after)

    '''
    Helpers
    '''

    def is_master(self, who):
        return who.id in self.masters

    async def boot(self):
        logger.info('Globibot is booting up...')
        await self.start(self.token)

    async def shutdown(self):
        await self.logout()

    '''
    Details
    '''

    @property
    def plugin_descriptors(self):
        enabled_plugins = self.config.get(c.ENABLED_PLUGINS_KEY)

        if enabled_plugins is None:
            enabled_plugins = {}

        return [
            (plugin_name, config)
            for plugin_name, config in enabled_plugins.items()
        ]

    def debug_message(self, message, event_type):
        logger.debug(
            '{:8} {:15.15} {:20} {}'.format(
                event_type,
                message.author.name,
                message.author.id,
                message.content
            )
        )

    def _dispatch_message(self, plugin_action, message, *args):
        # Ignoring our own messages
        if message.author.id == self.user.id:
            return

        # Filtering servers
        if message.server.name not in self.enabled_servers:
            return

        self._dispatch(plugin_action, message, *args)

    def _dispatch(self, plugin_action, *args):
        for plugin in self.plugin_collection.plugins:
            future = plugin_action(plugin, *args)
            ensure_future(future)
