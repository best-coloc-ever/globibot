from .validator import validator

from ..helpers.parsing import tokenize, BoundPair, TokenType

from funcparserlib.parser import NoParseError, _Tuple

# from utils.logging import logger

def command(parser, *args, **kwargs):

    def validate_parser(content):
        try:
            ignored_tokens = kwargs.get('ignored_tokens', (TokenType.Space, ))
            tokens = tokenize(content, ignores=ignored_tokens)
            # logger.debug(tokens)
            parsed = parser.parse(tokens)
            if type(parsed) is not _Tuple:
                parsed = (parsed,)
            # logger.debug(parsed)
            return True, dict([
                named for named in parsed
                if type(named) is BoundPair
            ])
        except NoParseError as e:
            # logger.error(e)
            return False, {}

    return validator(validate_parser, *args, **kwargs)
