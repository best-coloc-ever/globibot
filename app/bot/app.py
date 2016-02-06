from .globibot import Globibot

from . import constants as c
from . import modules

from os import getenv

def init_globibot(web_app):
    email = getenv(c.GLOBIBOT_EMAIL_KEY, c.GLOBIBOT_DEFAULT_EMAIL)
    password = getenv(c.GLOBIBOT_PASSWORD_KEY)

    if password is None:
        raise RuntimeError(
            "Please specify Globibot's credentials:\n"
            " - Globibot's email:    {}\n"
            " - Globibot's password: {}\n"
                .format(c.GLOBIBOT_EMAIL_KEY, c.GLOBIBOT_PASSWORD_KEY)
        )

    bot_modules = [
        modules.Hello,
        modules.Github,
        modules.Twitch,
        modules.Twitter,
    ]

    return Globibot(web_app, bot_modules, email, password)
