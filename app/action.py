import re

class Action:

    def __init__(self, description, pattern, handler, notify):
        self.description = description
        self.pattern = pattern
        self.handler = handler
        self.notify = notify
        self.match = None

    def matches(self, input):
        self.match = re.match(self.pattern, input)
        return self.match is not None

    def perform(self, channel):
        if self.match is not None:
            self.notify(channel, 'Attempting to `{}`'.format(self.description))
            try:
                output = self.handler(**self.match.groupdict())
                self.notify(channel, output)
            except Exception as e:
                self.notify(channel, 'Error: {}'.format(e))
