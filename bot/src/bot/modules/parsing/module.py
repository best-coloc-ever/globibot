from bot.lib.module import Module
from bot.lib.decorators import command
from bot.lib.helpers.parsing import exact_no_case, alpha_num, context, maybe, integer

class AdvancedParsing(Module):

    @command(exact_no_case('hi') + maybe(alpha_num >> context('who')))
    async def plop(self, message, who='anonymous'):
        await self.send_message(
            message.channel,
            'Hi {}'.format(who)
        )

    @command(integer >> context('n'))
    async def test(self, message, n=0):
        await self.send_message(
            message.channel,
            '{}: {}'.format(type(n), n)
        )
