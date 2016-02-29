from utils import json_config

from .globibot import Globibot
from .constants import CONFIG_FILE

import sys

def init_globibot(web_app):
    try:
        config_file = open(CONFIG_FILE, 'r')
    except IOError as e:
        sys.exit(
            'Error while opening required file: "{}"\n'
            '{}'
                .format(CONFIG_FILE, e)
        )

    with config_file:
        try:
            config = json_config.load(config_file)
        except Exception as e:
            sys.exit(
                'Error while parsing file: "{}"\n'
                '{}'
                    .format(CONFIG_FILE, e)
            )

    return Globibot(config, web_app)
