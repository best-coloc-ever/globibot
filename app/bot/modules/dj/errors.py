from ..base import ModuleException, EMOTES

from . import constants as c

class NotInvoked(ModuleException):

    def error(self, message):
        return (
            '{} I\'m not playing in any voice channels yet'
        ).format(
            message.author.mention
        )

class AlreadyInvoked(ModuleException):

    def __init__(self, channel):
        self.channel = channel

    def error(self, message):
        return (
            '{} I\'m already playing in another voice channel: {}'
        ).format(
            message.author.mention,
            self.channel
        )

class WrongChannel(ModuleException):

    def __init__(self, channel):
        self.channel = channel

    def error(self, message):
        return (
            '{} You\'re in the wrong channel\n'
            'Please use the `dj` commands in {}'
        ).format(
            message.author.mention,
            self.channel.mention
        )

class NotListening(ModuleException):

    def error(self, message):
        return (
            '{} You can\'t do that {}\n'
            'You\'re not even listening to me {}\n',
        ).format(
            message.author.mention,
            EMOTES.LirikNot,
            EMOTES.LirikFeels,
        )

class NonExistentChannel(ModuleException):

    def __init__(self, channel_name):
        self.channel_name = channel_name

    def error(self, message):
        return (
            '{} There is no channel named `{}` in this server'
        ).format(
            message.author.mention,
            self.channel_name
        )


class VoiceChannelJoinError(ModuleException):

    def __init__(self, exception):
        self.exception = exception

    def error(self, message):
        return (
            '{} I encountered an error while joining the voice channel:\n'
            '```\n'
            '{}\n'
            '```\n'
            '{}'
        ).format(
            message.author.mention,
            self.exception,
            EMOTES.LirikFeels
        )

class VoiceChannelLeaveError(ModuleException):

    def __init__(self, exception):
        self.exception = exception

    def error(self, message):
        return (
            '{} I encountered an error while leaving the voice channel:\n'
            '```\n'
            '{}\n'
            '```\n'
            '{}'
        ).format(
            message.author.mention,
            self.exception,
            EMOTES.LirikFeels
        )

class TooManyQueuedForUser(ModuleException):

    def error(self, message):
        return (
            '{} {} of your songs are already queued!\n'
            'Don\'t be selfish {}'
        ).format(
            message.author.mention,
            c.MAX_VIDEO_PER_USER,
            EMOTES.LirikNot
        )

class VideoTooLong(ModuleException):

    def error(self, message):
        return (
            '{} Your song is too long {}\n'
            'It cannot exceed {} seconds'
        ).format(
            message.author.mention,
            EMOTES.LirikNot,
            c.MAX_VIDEO_DURATION
        )

class YTDLExtractInfosError(ModuleException):

    def __init__(self, exception):
        self.exception = exception

    def error(self, message):
        return (
            '{} I was unable to extract information from your video\n'
            '```\n'
            '{}\n'
            '```'
        ).format(
            message.author.mention,
            self.exception
        )

class AlreadyQueued(ModuleException):

    def error(self, message):
        return (
            '{} This song is already queued {}'
        ).format(
            message.author.mention,
            EMOTES.LirikNot
        )
