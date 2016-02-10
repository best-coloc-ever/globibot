from ..base import Module, command, ModuleException, master_only

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
    async def master_only(self, message):
        await self.send_message(message.channel, 'Hi')
