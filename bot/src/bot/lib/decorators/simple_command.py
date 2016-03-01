from .validator import validator

from parse import parse

def simple_command(format, *args, **kwargs):

    def validate_format(content):
        parsed = parse(format, content)

        if parsed is None:
            return (False, {})

        return (True, parsed.named)

    return validator(validate_format, *args, **kwargs)
