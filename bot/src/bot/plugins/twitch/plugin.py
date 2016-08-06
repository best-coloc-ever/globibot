from bot.lib.plugin import Plugin
from bot.lib.decorators import command

from bot.lib.helpers import parsing as p
from bot.lib.helpers import formatting as f
from bot.lib.helpers.hooks import master_only

class Twitch(Plugin):

    def load(self):
        self.client_id = self.config.get(c.CLIENT_ID_KEY)

        if not self.client_id:
            self.warning('Missing client id: API calls might not work')


    @command(
        p.string('!twitch') + p.string('status')
                            + p.bind(p.word, 'channel'),
        master_only
    )
    async def twitch_status(self, message, channel):
        pass
