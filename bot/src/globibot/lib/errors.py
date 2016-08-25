class PluginException(Exception):

    def __init__(self):
        pass

    def error(self, message):
        raise NotImplemented
