"""
Use parse to convert a list of tokens into a parse tree
according to the Jack grammar specification
"""
from tokenizer import Token

OR = '^'

KEYWORD_CONSTANTS = (
    Token('keyword','true'),
    Token('keyword','false'),
    Token('keyword','null'),
    Token('keyword','this')
)

OPERATIONS = (
    Token('symbol','+'),
    Token('symbol','-'),
    Token('symbol','*'),
    Token('symbol','/'),
    Token('symbol','&'),
    Token('symbol','|'),
    Token('symbol','>'),
    Token('symbol','<'),
    Token('symbol','=')
)

UNARY_OPERATIONS = (
    Token('symbol','-'),
    Token('symbol','~')
)

class Parser(object):
    def __init__(tokens):
        self.tokens = tokens
        self.idx = 0

    def parse(self):
        return self.parse_class()

    def parse_class(self):
        class_node = Token('class', [])

        self.try_add(class_node, 'keyword', value='class')
        self.try_add(class_node, 'identifier')

        while self.is_class_var_declaration():
            node = self.parse_class_var_declaration()
            class_node.value.append(node)

        self.try_add(class_node, 'symbol', value='{')
        self.try_add(class_node, 'symbol', value='}')

        return class_node

    def is_class_var_declaration(self):
        return self.token in (
            Token('keyword', 'static'),
            Token('keyword', 'field')
        )

    def parse_class_var_declaration(self):
        dec_node = Token('classVarDec', [])

        try_add(class_node, tokens[idx], 'keyword', value='static^field')
        idx += 1
        
        node, idx = parse_type(tokens, idx)
        dec_node.append


    def parse_expression(self, token):
        Token('symbol','}')


    def parse_subroutine_call(self, token):
        pass

    def parse_op(self, token):
        if token in OPERATIONS:
            return token
        else:
            raise ValueError(token, 'is not a valid operation.')

    def parse_unary_op(self, token):
        if token in UNARY_OPERATIONS:
            return token
        else:
            raise ValueError(token, 'is not a valid unary operation.')

    def parse_keyword_constant(self, token):
        if token in KEYWORD_CONSTANTS:
            return token
        else:
            raise ValueError(token, 'is not a valid keyword constant.')

    def try_add(self, node, token, _type, value=None):
        assert (
            isinstance(self.token, Token),
            '{} {} must be a Token'.format(type(self.token), self.token)
        )
        assert isinstance(node.value, list), 'Node {} must have a list'.format(node)
        assert self.token.type == _type, 'Token {} must be type {}'.format(self.token, _type)
        if value:
            assert (
                self.token.value in value.split(OR), 
                'Token {} must have value {}'.format(self.token, value.split(OR))
            )
        self.idx += 1
        node.value.append(self.token)

    @property
    def token(self):
        return self.tokens[self.idx]