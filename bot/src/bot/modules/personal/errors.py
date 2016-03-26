from bot.lib.errors import ModuleException

class PrefixNotSubstring(ModuleException):

    def error(self, message):
        return (
            '{} your command prefix must be part of your current name!'
                .format(message.author.mention)
        )

class NoUrlsGiven(ModuleException):

    def error(self, message):
        return (
            '{} you need to specify at least one source URL'
                .format(message.author.mention)
        )

class FetchError(ModuleException):

    def __init__(self, url):
        self.url = url

    def error(self, message):
        return '{} I wasn\'t able to fetch the url: {}'.format(
            message.author.mention,
            self.url
        )

class NotAnImageError(ModuleException):

    def __init__(self, url):
        self.url = url

    def error(self, message):
        return '{} the url: {} doesn\'t seem to be an image'.format(
            message.author.mention,
            self.url
        )
