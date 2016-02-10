from .errors import ModuleException
from .discord import master_id, EMOTES

FORMAT_MAGIC_ATTR = 'command_formats'

def command(format, pre_hook=lambda: None):
    '''Intended to be used as a decorator
    Will add some metadata to the decorated function to hint the Module class to
    handle it as an action
    '''
    def wrapped(func):

        def call(module, message, *args, **kwargs):
            pre_hook(message)
            return func(module, message, *args, **kwargs)

        if hasattr(func, FORMAT_MAGIC_ATTR):
            formats = getattr(func, FORMAT_MAGIC_ATTR)
            formats.append(format)
            setattr(call, FORMAT_MAGIC_ATTR, formats)
        else:
            setattr(call, FORMAT_MAGIC_ATTR, [format])
        return call

    return wrapped

class NotMasterError(ModuleException):

    def error(self, message):
        return '{} You\'re not the boss of me {}'.format(
            message.author.mention,
            EMOTES.LirikNot
        )

def master_only(message):
    if message.author.id != master_id:
        raise NotMasterError
