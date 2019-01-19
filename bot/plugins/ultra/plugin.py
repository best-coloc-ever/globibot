from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command
from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import global_cooldown, user_cooldown, master_only

ULTRA_CHANNEL_ID = "426816034771566592"

class Ultra(Plugin):

    def load(self):
        pass

    @command(p.string('!dropinc'), master_only)
    async def dropinc(self, message):
        messages_to_delete = [
            m for m in self.bot.messages
            if m.channel.id == ULTRA_CHANNEL_ID
        ][-50:]
        await self.bot.delete_messages(messages_to_delete)
