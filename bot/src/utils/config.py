import yaml
import sys

BOT_CONFIG_KEY = 'bot'
WEB_CONFIG_KEY = 'web'
DB_CONFIG_KEY = 'db'

def load(file):
    try:
        config_file = open(file, 'r')
    except IOError as e:
        sys.exit(
            'Error while opening required file: "{}"\n'
            '{}'
                .format(file, e)
        )

    with config_file:
        try:
            config = yaml.load(config_file)
        except yaml.YAMLError as e:
            sys.exit(
                'Error while parsing file: "{}"\n'
                '{}'
                    .format(file, e)
            )

    return config

def load_config(file):
    config = load(file)

    try:
        bot_config = config[BOT_CONFIG_KEY]
        web_config = config[WEB_CONFIG_KEY]
        db_config  = config[DB_CONFIG_KEY]
    except KeyError as e:
        sys.exit(
            'Missing top level configuration key: "{}"'
                .format(e)
        )

    return (bot_config, web_config, db_config)
