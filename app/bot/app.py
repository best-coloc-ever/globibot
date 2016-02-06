from .globibot import Globibot
from . import constants as c
from . import modules

import os

def init_globibot():
    email = os.getenv(c.GLOBIBOT_EMAIL_KEY, c.GLOBIBOT_DEFAULT_EMAIL)
    password = os.getenv(c.GLOBIBOT_PASSWORD_KEY)

    if password is None:
        raise RuntimeError(
            "Please specify Globibot's credentials:\n"
            " - Globibot's email:    {}\n"
            " - Globibot's password: {}\n"
                .format(c.GLOBIBOT_EMAIL_KEY, c.GLOBIBOT_PASSWORD_KEY)
        )

    bot_modules = [

    ]

    return Globibot(bot_modules, email, password)
