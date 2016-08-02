from ..errors import ModuleException
from ..discord import EMOTES

class NotMasterError(ModuleException):

    def error(self, message):
        return '{} You\'re not the boss of me {}'.format(
            message.author.mention,
            EMOTES.LirikNot
        )

def master_only(bot, message):
    if not bot.is_master(message.author):
        raise NotMasterError
