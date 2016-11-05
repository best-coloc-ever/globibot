from funcparserlib.lexer import make_tokenizer
from funcparserlib import parser as p

from collections import namedtuple
from re import DOTALL

class TokenType:
    Space = 'SPACE'
    Integer = 'INTEGER'
    Float = 'FLOAT'
    Mention = 'MENTION'
    Channel = 'CHANNEL'
    Emoji = 'EMOJI'
    Snippet = 'SNIPPET'
    Word = 'WORD'

TOKEN_SPEC = [
    (TokenType.Space,   (r'\s+',)),
    (TokenType.Float,   (r'[+-]?[0-9]*\.[0-9]+',)),
    (TokenType.Integer, (r'[+-]?[0-9]+',)),
    (TokenType.Mention, (r'<@!?[0-9]+>',)),
    (TokenType.Channel, (r'<#[0-9]+>',)),
    (TokenType.Emoji,   (r'<:\S+:[0-9]+>',)),
    (TokenType.Snippet, (r'```\S+\n(.*?)```', DOTALL)),
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
to_f = lambda tok: float(tok.value)
to_s = lambda tok: str(tok.value)
to_a = lambda toks: [tok.value for tok in toks]
const = lambda value: lambda _: value

def extract_mention_id(tok):
    if '!' in tok.value:
        return int(tok.value[3:-1])
    else:
        return int(tok.value[2:-1])

def extract_channel_id(tok):
    return int(tok.value[2:-1])

def extract_emoji_id(tok):
    start_idx = tok.value.rfind(':') + 1
    end_idx = tok.value.rfind('>')
    return int(tok.value[start_idx:end_idx])

Snippet = namedtuple('Snippet', ['language', 'code'])
def extract_snippet(tok):
    val = tok.value
    new_line_idx = val.index('\n')

    return Snippet(
        language = val[3:new_line_idx].lower(),
        code     = val[new_line_idx + 1:-3]
    )

# Parsers
def not_parser(parser):

    @p.Parser
    def _not_parser(tokens, s):
        if s.pos >= len(tokens):
            raise p.NoParseError('no tokens left in the stream', s)
        try:
            parser.run(tokens, s)
        except p.NoParseError:
            pos = s.pos + 1
            s2 = p.State(pos, max(pos, s.max))
            return None, s2
        else:
            raise p.NoParseError('parsing failed', s)

    _not_parser.name = '!{}'.format(parser.name)

    return _not_parser

a         = lambda value: p.some(lambda tok: tok.value == value)
string    = lambda s: p.some(lambda tok: tok.value.lower() == s.lower()) .named(s)
some_type = lambda t: p.some(lambda tok: tok.type == t)                  .named(t)
not_type  = lambda t: p.some(lambda tok: tok.type != t)                  .named('!{}'.format(t))
any_type  = p.some(lambda _: True)                                       .named('Any')

eof     = p.finished                        .named('')
some    = p.some
maybe   = lambda parser: p.maybe(parser)    .named('[{}]'.format(parser.name))
many    = lambda parser: p.many(parser)     .named('[{}]...'.format(parser.name))
skip    = lambda parser: p.skip(parser)     .named('')
oneplus = lambda parser: p.oneplus(parser)  .named('{},[{}]...'.format(parser.name, parser.name))
sparsed = lambda parser: (skip(many(not_parser(parser))) + parser)\
                                            .named('_{}'.format(parser.name))

integer = (some_type(TokenType.Integer) >> to_i)               .named('I')
number  = (
    (   some_type(TokenType.Integer)
    |   some_type(TokenType.Float)
    )
    >> to_f)                                                   .named('N')
word    = (some_type(TokenType.Word)    >> to_s)               .named('W')
mention = (some_type(TokenType.Mention) >> extract_mention_id) .named('M')
channel = (some_type(TokenType.Channel) >> extract_channel_id) .named('C')
emoji   = (some_type(TokenType.Emoji)   >> extract_emoji_id)   .named('E')
snippet = (some_type(TokenType.Snippet) >> extract_snippet)    .named('S')

# High level helpers
on_off_switch = (
    (string('on')  >> const(True) ) |
    (string('off') >> const(False))
)

url = p.some(
    lambda tok: tok.type == TokenType.Word and tok.value.startswith('http')
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
    return (transformed >> bind_expr).named('<{}#{}>'.format(name, transformed.name))
