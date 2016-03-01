from .validator import validator

from ..helpers.parsing import tokenize, ContextualPair

from funcparserlib.parser import NoParseError

# from utils.logging import logger

def command(parser, *args, **kwargs):

    def validate_parser(content):
        try:
            tokens = tokenize(content)
            # logger.debug(tokens)
            parsed = parser.parse(tokens)
            if not type(parsed) is list:
                parsed = [parsed]
            # logger.debug(parsed)
            return True, dict([
                named for named in parsed
                if type(named) is ContextualPair
            ])
        except NoParseError as e:
            # logger.error(e)
            return False, {}

    return validator(validate_parser, *args, **kwargs)
