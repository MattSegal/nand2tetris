"""
Use tokenize() to convert a string into a list of tokens
"""

import re
from constants import KEYWORDS, SYMBOLS

MULTILINE_COMMENT_REGEX = r'\/\*[\s\S]*?\*\/'
COMMENT_REGEX = r'\/\/[\s\S]*'
IDENTIFIER_REGEX = r'([A-Z|a-z|_]){1}([A-Z|a-z|0-9|_])*'
WHITESPACE = (' ', '\t', '\n', '\r')

def tokenize(text):
    tokens = []
    text = re.sub(MULTILINE_COMMENT_REGEX, '', text)
    for line in text.split('\n'):
        line = re.sub(COMMENT_REGEX, '', line)
        tokens += extract_tokens(line)
    return tokens

def extract_tokens(line):
    tokens = []
    word = ''
    is_string = False
    for i, c in enumerate(line):
        # Handle strings, which can span whitespace
        if c == '"':
            if is_string:
                tokens.append(Token('stringConstant', word))
                word = ''
                is_string = False
            else:
                is_string = True
            continue

        # Grow the word
        if is_string or (c not in WHITESPACE and c not in SYMBOLS):
            word += c
            if i < len(line) - 1:
                continue
        
        # Handle keywords, identifiers, ints, strings
        if word:
            if word in KEYWORDS:
                tokens.append(Token('keyword', word))
            elif str.isdigit(word):
                tokens.append(Token('integerConstant', word))
            elif is_valid_identifier(word):
                tokens.append(Token('identifier', word))
            else:
                raise ValueError(word, 'is not a valid identifier.')
            word = ''

        # Handle symbols, which may not have whitespace
        if c in SYMBOLS:
            tokens.append(Token('symbol', c))

    if is_string:
        raise ValueError('String constant did not terminate')
    return tokens

def is_valid_identifier(word):
    return bool(re.match(IDENTIFIER_REGEX, word))


class Token(object):
    def __init__(self, _type, value):
        self.type = _type
        self.value = value

    def append(self, val):
        print val
        self.value.append(val)

    def __repr__(self):
        return '< {} {} >'.format(self.type, self.value)

    def __eq__(self, other):
        return (
            self.type == other.type and 
            self.value == other.value
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)