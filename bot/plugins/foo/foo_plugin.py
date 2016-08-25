from globibot.lib.plugin import Plugin

from globibot.lib.decorators import command # Command declaration helper

from globibot.lib.helpers import parsing as p # Parser combinator tools
from globibot.lib.helpers.hooks import master_only # Command hook to only allow masters

class Foo(Plugin):

    def load(self):
        '''
        Called on plugin load/reload
        '''

        # Loads the value of the `bar` configuration key with a default value
        # if the key were to be absent
        self.bar = self.config.get('bar', 42)

    @command(p.string('!foo') + p.bind(p.integer, 'number'))
    async def foo_command(self, message, number):
        '''
        Called on inputs starting with the string '!foo' (case insensitive)
        followed by an integer whose value will be bound to the `number`
        variable
        '''

        await self.send_message(
            message.channel, # Sends a message in the same channel as the input
            '{} * {} = {}'.format(number, self.bar, number * self.bar)
        )

    @command(p.string('!id') + p.bind(p.mention, 'user_id'), master_only)
    async def id_command(self, message, user_id):
        '''
        Called on inputs starting with the string '!id' (case insensitive)
        followed by a discord user mention (usually displayed '@SomeUser' on
        discord's client)

        We have access to SomeUser's discord's ID in the `user_id` variable

        The command is marked as `master_only` and will execute only if the
        input was sent by someone who was registered as 'master' in the
        configuration file
        '''

        await self.send_message(
            message.channel,
            '{}: the id is {}'
                .format(message.author.mention, user_id),
            delete_after = 30 # Message deletes itself after 30 seconds
        )
