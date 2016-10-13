from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import master_only

from . import constants as c

import re

class Help(Plugin):

    def load(self):
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

        plugin = self.get_plugin(plugin_name)

        def hooks_description(hooks):
            if hooks:
                hook_descriptions = (
                    hook.__doc__.strip() for hook in hooks
                    if hook.__doc__
                )
                return '/* {} */'.format(' | '.join(hook_descriptions))
            return ''

        raw_components =[
            '{}{}'.format(
                validator.parser.name,
                hooks_description(validator.hooks)
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

    def get_plugin(self, name):
        return next(
            plugin for plugin in [
                reloader.plugin for reloader in
                self.bot.plugin_collection.plugin_reloaders
                if reloader.name == name
            ]
        )
