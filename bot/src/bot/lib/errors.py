from .discord import EMOTES

def unexpected_error_str(message, tb):
    context = {
        'sender': message.author.mention,
        'sad': EMOTES.LirikFeels,
        'heart': EMOTES.LirikH,
        'error': tb
    }

    string = (
        '{sender} Your command broke me {sad}\n'
        'Please notify my master of the following error {heart}:\n'
        '```python\n'
        '{error}\n'
        '```'
    )

    return string.format(**context)

def unexpected_async_error_str(tb):
    context = {
        'sad': EMOTES.LirikFeels,
        'heart': EMOTES.LirikH,
        'error': tb
    }

    string = (
        'Something asynchronous broke {sad}\n'
        'Please notify my master of the following error {heart}:\n'
        '```python\n'
        '{error}\n'
        '```'
    )

    return string.format(**context)


class ModuleException(Exception):

    def __init__(self, ):
        pass

    def error(self, message):
        raise NotImplemented

