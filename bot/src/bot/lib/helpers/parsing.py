from funcparserlib.lexer import make_tokenizer
from funcparserlib.parser import *

class TokenType:
    Space = 'SPACE'
    Char = 'CHAR'
    AlphaNum = 'ALPHA_NUM'
    Integer = 'INTEGER'

TOKEN_SPEC = [
    (TokenType.Space,    (r'[ \t\r\n]+',)),
    (TokenType.Char,     (r'#[0-9]+',)),
    (TokenType.AlphaNum, (r'[A-Za-z_][A-Za-z_0-9]*',)),
    (TokenType.Integer,  (r'[0-9]+',)),
]

tokenizer = make_tokenizer(TOKEN_SPEC)
tokenize = lambda string: list(
    token for token in tokenizer(string)
    if token.type not in [TokenType.Space]
)

exact = lambda value: some(lambda tok: tok.value == value)
exact_no_case = lambda value: some(lambda tok: tok.value.lower() == value.lower())

some_type = lambda t: some(lambda tok: tok.type == t)
alpha_num = some_type(TokenType.AlphaNum)
integer = some_type(TokenType.Integer)
char = some_type(TokenType.Char)

class ContextualPair(tuple):
    pass

context = lambda name: lambda tok: ContextualPair((name, tok.value))
