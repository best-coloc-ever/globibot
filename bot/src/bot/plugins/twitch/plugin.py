from bot.lib.plugin import Plugin
from bot.lib.decorators import command

from bot.lib.helpers import parsing as p
from bot.lib.helpers import formatting as f
from bot.lib.helpers.hooks import master_only

class Twitch(Plugin):

    def load(self):
        pass

    @command(
        p.string('!twitch') + p.string('status')
                            + p.bind(p.word, 'channel'),
        master_only
    )
    async def twitch_status(self, message, channel):
        pass
