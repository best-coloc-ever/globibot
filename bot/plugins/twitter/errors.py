from globibot.lib.errors import PluginException

class UserNotFound(PluginException):

    def __init__(self, name):
        self.name = name

    def error(self, message):
        return 'Unable to find a channel named `{}`'.format(self.name)
