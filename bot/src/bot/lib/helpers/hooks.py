from ..errors import ModuleException
from ..discord import EMOTES
from ..constants import MASTER_IDS_KEY

class NotMasterError(ModuleException):

    def error(self, message):
        return '{} You\'re not the boss of me {}'.format(
            message.author.mention,
            EMOTES.LirikNot
        )

def master_only(bot, message):
    master_ids = bot.config.get(MASTER_IDS_KEY, [])

    if message.author.id not in master_ids:
        raise NotMasterError
