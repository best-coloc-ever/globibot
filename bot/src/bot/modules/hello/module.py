from ..base import Module, command, ModuleException, master_only

import asyncio

class HelloError(ModuleException):

    def error(self, message):
        return "Hello error {}".format(message.author.mention)

class Hello(Module):

    @command('Hello')
    @command('Hi')
    @command('Hej')
    async def hello(self, message):
        self.info('Saluting {}...'.format(message.author.name))

        await self.send_message(
            message.channel,
            'Hej {}'.format(message.author.mention)
        )

    @command('Error')
    async def error(self, message):
        raise HelloError()

    @command('Crash')
    async def crash(self, message):
        error

    @command('Master', master_only)
    async def master_only_cmd(self, message):
        await self.send_message(message.channel, 'Hi')

    @command('Async', master_only)
    async def async_cmd(self, message):

        async def async_crash():
            await asyncio.sleep(5)
            raise Exception('Crashed :(')

        self.run_async(
            async_crash(),
            message.channel
        )
