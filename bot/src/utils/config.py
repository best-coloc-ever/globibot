import yaml
import sys

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
