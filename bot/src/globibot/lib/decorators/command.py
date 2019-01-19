from .validator import validator

from ..helpers.parsing import tokenize, BoundPair, TokenType

from funcparserlib.parser import NoParseError, _Tuple

def command(parser, *args, **kwargs):

    def validate_parser(content):
        try:
            ignored_tokens = kwargs.get('ignored_tokens', (TokenType.Space, ))
            tokens = tokenize(content, ignores=ignored_tokens)
            parsed = parser.parse(tokens)

            if type(parsed) is not _Tuple:
                parsed = (parsed,)

            return True, dict([
                named for named in parsed
                if type(named) is BoundPair
            ])
        except NoParseError:
            return False, {}
        except Exception as e:
            print('FAIL TO PARSE {}: {} {}'.format(repr(e), e, parser.name))
            return False, {}

    # For introspection
    validate_parser.parser = parser

    return validator(validate_parser, *args, **kwargs)
