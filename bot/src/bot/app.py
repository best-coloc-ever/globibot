from utils.config import load

from .globibot import Globibot
from .constants import BOT_CONFIG_KEY, CONFIG_FILE

import sys

def init_globibot(web_app):
    try:
        config = load(CONFIG_FILE)
        bot_config = config[BOT_CONFIG_KEY]
    except KeyError:
        sys.exit(
            'Missing top level configuration key: {}'
                .format(BOT_CONFIG_KEY)
        )

    return Globibot(bot_config, web_app)
