from ..errors import PluginException

from time import time
from collections import defaultdict

class NotMasterError(PluginException):

    def error(self, message):
        return (
            '{} You\'re not the boss of me'
                .format(message.author.mention)
        )

def master_only(bot, message):
    '''
    Master only
    '''
    return bot.is_master(message.author)

def master_only_verbose(bot, message):
    '''
    Master only
    '''
    if not bot.is_master(message.author):
        raise NotMasterError
    return True

def user_cooldown(seconds, verbose=False):
    cache = defaultdict(lambda: 0)

    def call(bot, message):
        now = time()
        last_used = cache[message.author.id]
        if now - last_used >= seconds:
            cache[message.author.id] = now
            return True
        if verbose:
            raise InCooldownError(seconds - (now - last_used))
        return False

    call.__doc__ = 'User cooldown {}s'.format(seconds)
    return call

class InCooldownError(PluginException):

    def __init__(self, usable_in):
        self.usable_in = usable_in

    def error(self, message):
        return (
            '{} calm down cowboy 🤠 (command usable in `{:.2f}` seconds)'
                .format(message.author.mention, self.usable_in)
        )

def global_cooldown(seconds, verbose=False):
    cache = defaultdict(lambda: 0)

    def call(bot, message):
        now = time()
        last_used = cache[message.channel.id]
        if now - last_used >= seconds:
            cache[message.channel.id] = now
            return True
        if verbose:
            raise InCooldownError(seconds - (now - last_used))
        return False

    call.__doc__ = 'Global cooldown {}s'.format(seconds)
    return call
