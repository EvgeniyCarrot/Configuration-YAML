import re 

TOKENS = [
    ('COMMENT', r'#.*'),
    ('QUESTION', r'\?'),    
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'), 
    ('IS', r'is'),
    ('QSTRING', r'q\([^)]*\)'),
    ('NUMBER', r'-?(?:\d+|\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?'),
    ('NAME', r'[a-z]+'),
    ('DOT', r'\.'),
    ('LBRACK', r'\['),
    ('RBRACK', r'\]'),
    ('OP', r'[+\-*/]'),
    ('FUNC', r'(len|mod)'),
    ('WHITESPACE', r'\s+'),
]

TOKEN_RE = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKENS)

def tokenize(text):
    for match in re.finditer(TOKEN_RE, text, re.DOTALL):
        kind = match.lastgroup
        value = match.group()
        if kind in ('WHITESPACE', 'COMMENT'):
            continue
        if kind == 'QSTRING':
            value = value[2:-1]  # remove q(...)
        yield (kind, value, match.start())