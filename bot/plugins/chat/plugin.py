from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers.hooks import master_only

from json import loads as json_loads

import apiai

class ChatBot(Plugin):

    def load(self):
        #self.ai = apiai.ApiAI(self.config.get('APIAI_ACCESS_TOKEN'))
        self.ai = apiai.ApiAI('13381aedc4e5471498f7c79a9c058dab')

    @command(
        p.bind(p.mention, 'user') + p.bind((p.many(p.any_type >> p.to_s)), 'words'), master_only
    )
    async def answer(self, message, user, words):
        if str(user) != self.bot.user.id:
            return

        await self.bot.send_typing(message.channel)
        request = self.ai.text_request()
        request.session_id = 'discord_master_{}'.format(message.channel.id)
        request.query = ' '.join(words)

        response = request.getresponse()
        try:
            response_data = json_loads(response.read().decode())
            self.debug(response_data)
            speech = response_data['result']['fulfillment']['speech']
        except:
            pass
        else:
            await self.send_message(
                message.channel,
                speech
            )
