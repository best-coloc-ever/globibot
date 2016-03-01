from funcparserlib.lexer import make_tokenizer
from funcparserlib.parser import *

class TokenType:
    Space = 'SPACE'
    Integer = 'INTEGER'
    Word = 'WORD'

TOKEN_SPEC = [
    (TokenType.Space,   (r'\s+',)),
    (TokenType.Integer, (r'[0-9]+',)),
    (TokenType.Word,    (r'\S+',)), # Word is currently a catch-all
]

tokenizer = make_tokenizer(TOKEN_SPEC)
tokenize = lambda string: list(
    token for token in tokenizer(string)
    if token.type not in [TokenType.Space]
)

exact = lambda value: some(lambda tok: tok.value == value)
exact_no_case = lambda value: some(lambda tok: tok.value.lower() == value.lower())

def to_i(tok):
    try:
        tok.value = int(tok.value)
    except:
        pass

    return tok

some_type = lambda t: some(lambda tok: tok.type == t)
integer = some_type(TokenType.Integer) >> to_i
word = some_type(TokenType.Word)

class ContextualPair(tuple):
    pass

context = lambda name: lambda tok: ContextualPair((name, tok.value))
