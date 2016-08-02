from bot.lib.plugin import Plugin
from bot.lib.decorators import command

from bot.lib.helpers import parsing as p
from bot.lib.helpers import formatting as f
from bot.lib.helpers.hooks import master_only

from . import constants as c

import re

class Help(Plugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.enabled_plugins_names = self.config.get(c.ENABLED_PLUGINS_KEY, [])

    '''
    Commands
    '''

    help_prefix = p.string('!help')

    @command(help_prefix + p.eof)
    async def general_help(self, message):
        help_message = f.code_block(
            [
                '!help {}'.format(name) for name in
                self.enabled_plugins_names
            ],
            language='css' # Kinda look ok
        )

        await self.send_message(
            message.channel,
            '{}\n{}'.format(message.author.mention, help_message),
            delete_after=30
        )

    @command(help_prefix + p.bind(p.word, 'plugin_name'))
    async def plugin_help(self, message, plugin_name):
        plugin_name = plugin_name.lower()

        if plugin_name not in self.enabled_plugins_names:
            return

        plugin = next(
            p for p in self.plugins
            if p.__class__.__name__.lower() == plugin_name
        )

        raw_components =[
            '{}{}'.format(
                validator.parser.name,
                ' /* master only */' if validator.pre_hook == master_only else ''
            )
            for validator, _ in plugin.actions
        ]
        components = sorted(
            re.sub(' +',' ', re.sub(r'[(,)]', '', name)).split(' ')
            for name in raw_components
        )

        lines = [
            ' '.join(comp) for comp in components
        ]

        help_message = f.code_block(lines, language='css')

        await self.send_message(
            message.channel,
            '{} `{}` plugin commands:\n\n{}'
                .format(message.author.mention, plugin_name, help_message),
            delete_after=30
        )

    '''
    Internals
    '''

    @property
    def plugins(self):
        return [
            plugin for plugin in self.bot.plugin_collection.plugins
            if plugin.__class__.__name__.lower() in self.enabled_plugins_names
        ]
