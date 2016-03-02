from funcparserlib.lexer import make_tokenizer
from funcparserlib import parser as p

class TokenType:
    Space = 'SPACE'
    Integer = 'INTEGER'
    Word = 'WORD'

TOKEN_SPEC = [
    (TokenType.Space,   (r'\s+',)),
    (TokenType.Integer, (r'[0-9]+',)),
    (TokenType.Word,    (r'\S+',)), # Word is currently a catch-all
]

default_tokenizer = make_tokenizer(TOKEN_SPEC)

def tokenize(string, tokenizer=default_tokenizer, ignores=(TokenType.Space,)):
    return [
        token for token in tokenizer(string)
        if token.type not in ignores
    ]

# Transformers
to_i = lambda tok: int(tok.value)
to_s = lambda tok: str(tok.value)
to_a = lambda toks: [tok.value for tok in toks]
const = lambda value: lambda _: value

# Parsers
a = lambda value: p.some(lambda tok: tok.value == value)
string = lambda s: p.some(lambda tok: tok.value.lower() == s.lower())
some_type = lambda t: p.some(lambda tok: tok.type == t)
any_type = p.some(lambda _: True)

maybe = p.maybe
many = lambda parser: p.many(parser) >> to_a
integer = some_type(TokenType.Integer) >> to_i
word = some_type(TokenType.Word) >> to_s

# High level helpers
on_off_switch = (
    (string('on')  >> const(True) ) |
    (string('off') >> const(False))
)

def int_range(low, high):

    def predicate(token):
        if token.type != TokenType.Integer:
            return False
        return to_i(token) in range(low, high + 1)

    return p.some(predicate) >> to_i

def one_of(parser, first, *rest):
    combined_parser = parser(first)

    for possibility in rest:
        combined_parser = combined_parser | parser(possibility)

    return combined_parser

# Context
class BoundPair(tuple): pass

def bind(transformed, name):
    bind_expr = lambda value: BoundPair((name, value)) if value is not None else None
    return transformed >> bind_expr
