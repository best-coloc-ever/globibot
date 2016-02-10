from .discord import EMOTES, master

def unexpected_error_str(message, tb):
    context = {
        'sender': message.author.mention,
        'sad': EMOTES.LirikFeels,
        'master': master,
        'heart': EMOTES.LirikH,
        'error': tb
    }

    string = (
        '{sender} Your command broke me {sad}\n'
        'Please notify my master {master} of the following error {heart}:\n'
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

