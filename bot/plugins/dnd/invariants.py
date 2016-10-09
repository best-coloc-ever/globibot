from globibot.lib.errors import PluginException

MAX_DICE_COUNT = 10

class TooManyDiceError(PluginException):

    def __init__(self, count):
        self.count = count

    def error(self, message):
        return (
            'You attempted to roll too many dice ({})\n'
            'You cannot roll more than {} dice'
                .format(self.count, MAX_DICE_COUNT)
        )

MAX_D20_COUNT = 1 # For now

class TooManyD20sError(PluginException):

    def __init__(self, count):
        self.count = count

    def error(self, message):
        return (
            'You attempted to roll too many d20s ({})\n'
            'You cannot roll more than {} d20'
                .format(self.count, MAX_D20_COUNT)
        )

MODIFIER_MIN_BOUND = -20
MODIFIER_MAX_BOUND = 20

class ModifierOutOfBounds(PluginException):

    def __init__(self, count):
        self.count = count

    def error(self, message):
        return (
            'The modifier value is out of bound ({})\n'
            'Its value should be between {} and {}'
                .format(self.count, MODIFIER_MIN_BOUND, MODIFIER_MAX_BOUND)
        )
