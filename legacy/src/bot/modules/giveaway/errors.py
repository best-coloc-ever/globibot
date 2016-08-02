from bot.lib.errors import ModuleException
from bot.lib.discord import EMOTES

class NotPrivateChannel(ModuleException):

    def error(self, message):
        return (
            '{}: You should PM me to register a giveaway'
        ).format(
            message.author.mention
        )

class NotPublicChannel(ModuleException):

    def error(self, message):
        return (
            '{}: You must start your giveaway in a public channel!'
        ).format(
            message.author.mention
        )

class NoCurrentGiveaway(ModuleException):

    def error(self, message):
        return (
            'You have no current giveaway\n'
            'Use the `!giveaway content *your content*` '
            'command to register a giveaway'
        )

class IncorrectGiveaway(ModuleException):

    def error(self, message):
        return (
            '{}: You did not register a giveaway!'
        ).format(
            message.author.mention
        )

class AlreadyInProgress(ModuleException):

    def error(self, message):
        return (
            '{}: There is already a giveaway in progress!'
        ).format(
            message.author.mention
        )

class CantJoinYourOwnGiveaway(ModuleException):

    def error(self, message):
        return (
            '{}: You can\'t join your own giveaway you silly {}'
        ).format(
            message.author.mention,
            EMOTES.LirikF
        )
