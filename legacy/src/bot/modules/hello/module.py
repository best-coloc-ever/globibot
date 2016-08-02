from bot.lib.module import Module
from bot.lib.errors import ModuleException
from bot.lib.decorators import simple_command
from bot.lib.helpers.hooks import master_only

import asyncio

class HelloError(ModuleException):

    def error(self, message):
        return "Hello error {}".format(message.author.mention)

class Hello(Module):

    @simple_command('Hello')
    @simple_command('Hi')
    @simple_command('Hej')
    async def hello(self, message):
        self.info('Saluting {}...'.format(message.author.name))

        await self.send_message(
            message.channel,
            'Hej {}'.format(message.author.mention)
        )

    @simple_command('Error')
    async def error(self, message):
        raise HelloError()

    @simple_command('Crash')
    async def crash(self, message):
        error

    @simple_command('Master', master_only)
    async def master_only_cmd(self, message):
        await self.send_message(message.channel, 'Hi')

    @simple_command('Async', master_only)
    async def async_cmd(self, message):

        async def async_crash():
            await asyncio.sleep(5)
            raise Exception('Crashed :(')

        self.run_async(
            async_crash(),
            message.channel
        )
