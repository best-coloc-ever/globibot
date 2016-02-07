from ..base import Module, command

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
