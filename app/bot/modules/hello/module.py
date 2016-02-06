from ..base import Module, command

class Hello(Module):

    @command('Hello')
    async def hello(self, message):
        await self.respond('Hi there {}'.format(message.author.name))
