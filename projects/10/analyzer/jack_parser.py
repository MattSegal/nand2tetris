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
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0

    def parse(self):
        return self.parse_class()

    def parse_class(self):
        """
        'class' className '{' classVarDec* subroutineDec* '}' 
        """
        node = Token('class', [])

        self.try_add(node, 'keyword', value='class')
        self.try_add(node, 'identifier')
        self.try_add(node, 'symbol', value='{')

        while self.is_class_var_declaration():
            node.append(self.parse_class_var_declaration())

        while self.is_subroutine_declaration():
            node.append(self.parse_subroutine_declaration())

        self.try_add(node, 'symbol', value='}')

        return node

    def is_class_var_declaration(self):
        return self.token in (
            Token('keyword', 'static'),
            Token('keyword', 'field')
        )

    def parse_class_var_declaration(self):
        """
        ('static' | 'field' ) type varName (',' varName)* ';' 
        """
        node = Token('classVarDec', [])
        self.try_add(node, 'keyword', value='static^field')
        node.append(self.parse_type())

        self.try_add(node, 'identifier')

        while self.token.value == ',':
            self.try_add(node, 'symbol', value=',')
            self.try_add(node, 'identifier')
 
        self.try_add(node, 'symbol', value=';')
        return node

    def is_subroutine_declaration(self):
        return self.token in (
            Token('keyword', 'constructor'),
            Token('keyword', 'function'),
            Token('keyword', 'method')
        )

    def parse_subroutine_declaration(self):
        node = Token('subroutineDec', [])
        self.try_add(node, 'keyword', value='constructor^function^method')
        
        if self.token.value == 'void':
            self.try_add(node, 'keyword', value='void')
        else:
            node.append(self.parse_type())
        self.try_add(node, 'identifier')
        self.try_add(node, 'symbol', value='(')
        node.append(self.parse_parameter_list())
        self.try_add(node, 'symbol', value=')')
        node.append(self.parse_subroutine_body())
        return node

    def parse_subroutine_body(self):
        node = Token('subroutineBody', [])
        self.try_add(node, 'symbol', value='{')

        while self.token.value == 'var':
            node.append(self.parse_var_declaration())

        node.append(self.parse_statements())
        self.try_add(node, 'symbol', value='}')
        return node


    def parse_var_declaration(self):
        node = Token('varDec', [])
        self.try_add(node, 'keyword', value='var')
        node.append(self.parse_type())
        self.try_add(node, 'identifier')
        while self.token.value == ',':
            self.try_add(node, 'symbol', value=',')
            self.try_add(node, 'identifier')
        self.try_add(node, 'symbol', value=';')
        return node

    def parse_parameter_list(self):
        node = Token('parameterList', [])
        if self.token.value != ')':
            node.append(self.parse_type())
            self.try_add(node, 'identifier')
            while self.token.value == ',':
                node.append(self.parse_type())
                self.try_add(node, 'symbol', value=',')
                self.try_add(node, 'identifier')
        return node


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

    def try_add(self, node, _type, value=None):
        assert isinstance(self.token, Token), '{} {} must be a Token'.format(type(self.token), self.token)
        assert isinstance(node.value, list), 'Node {} must have a list'.format(node)
        assert self.token.type == _type, 'Token {} must be type {}'.format(self.token, _type)
        if value:
            assert self.token.value in value.split(OR), 'Token {} must have value {}'.format(self.token, value.split(OR))
        node.append(self.token)
        self.idx += 1

    @property
    def token(self):
        return self.tokens[self.idx]