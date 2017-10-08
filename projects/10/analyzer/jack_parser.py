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
                self.try_add(node, 'symbol', value=',')
                node.append(self.parse_type())
                self.try_add(node, 'identifier')
        return node


    def parse_statements(self):
        node = Token('statements', [])
        while self.is_statement():
            if self.token == Token('keyword', 'let'):
                node.append(self.parse_let_statement())
            elif self.token == Token('keyword', 'if'):
                node.append(self.parse_if_statement())
            elif self.token == Token('keyword', 'while'):
                node.append(self.parse_while_statement())
            elif self.token == Token('keyword', 'do'):
                node.append(self.parse_do_statement())
            elif self.token == Token('keyword', 'return'):
                node.append(self.parse_return_statement())
        return node

    def is_statement(self):
        return self.token in (
            Token('keyword', 'let'), 
            Token('keyword', 'if'),
            Token('keyword', 'while'),
            Token('keyword', 'do'),   
            Token('keyword', 'return')
        )

    def parse_let_statement(self):
        node = Token('letStatement', [])
        self.try_add(node, 'keyword', value='let')
        self.try_add(node, 'identifier')
        if self.token.value == '[':
            self.try_add(node, 'symbol', value='[')
            node.append(self.parse_expression())
            self.try_add(node, 'symbol', value=']')
        self.try_add(node, 'symbol', value='=')
        node.append(self.parse_expression())
        self.try_add(node, 'symbol', value=';')
        return node

    def parse_if_statement(self):
        node = Token('ifStatement', [])
        self.try_add(node, 'keyword', value='if')
        self.try_add(node, 'symbol', value='(')
        node.append(self.parse_expression())
        self.try_add(node, 'symbol', value=')')
        self.try_add(node, 'symbol', value='{')
        node.append(self.parse_statements())
        self.try_add(node, 'symbol', value='}')
        if self.token.value == 'else':
            self.try_add(node, 'keyword', value='else')
            self.try_add(node, 'symbol', value='{')
            node.append(self.parse_statements())
            self.try_add(node, 'symbol', value='}')
        return node


    def parse_while_statement(self):
        node = Token('whileStatement', [])
        self.try_add(node, 'keyword', value='while')
        self.try_add(node, 'symbol', value='(')
        node.append(self.parse_expression())
        self.try_add(node, 'symbol', value=')')
        self.try_add(node, 'symbol', value='{')
        node.append(self.parse_statements())
        self.try_add(node, 'symbol', value='}')
        return node

    def parse_do_statement(self):
        node = Token('doStatement', [])
        self.try_add(node, 'keyword', value='do')
        node.append(self.parse_subroutine_call())
        self.try_add(node, 'symbol', value=';')
        return node

    def parse_return_statement(self):
        node = Token('returnStatement', [])
        self.try_add(node, 'keyword', value='return')
        if self.token.value != ';':
            node.append(self.parse_expression())
        self.try_add(node, 'symbol', value=';')
        return node

    def parse_type(self):
        """
        'int' | 'char' | 'boolean' | identifier 
        """
        standard_types = (
            Token('keyword', 'int'), 
            Token('keyword', 'char'),
            Token('keyword', 'boolean')
        )

        if not self.token in standard_types:
            # Hack to validate identifier
            self.try_add(Token('dummy',[]), 'identifier')
        else:
            self.idx += 1
        return self.token

    def parse_expression(self):
        """
        term (op term)*
        """
        node = Token('expression', [])
        node.append(self.parse_term())
        while self.token in OPERATIONS:
            node.append(self.token)
            self.idx += 1
            node.append(self.parse_term())
        return node        

    def parse_term(self):
        """
        integerConstant | stringConstant | keywordConstant | 
        identifier | identifier '[' expression ']' | 
        subroutineCall | '(' expression ')' | (unaryOp term)
        """
        node = Token('term', [])
        # integerConstant | stringConstant
        if self.token.type in ('integerConstant', 'stringConstant'):
            node.append(self.token)
            self.idx += 1
        # keywordConstant
        elif self.token in KEYWORD_CONSTANTS:
            node.append(self.token)
            self.idx += 1
        # unaryOp term
        elif self.token in UNARY_OPERATIONS:
            node.append(self.token)
            self.idx += 1
            node.append(self.parse_term())
        # '(' expression ')'
        elif self.token.value == '(':
            self.try_add(node, 'symbol', '(')
            node.append(self.parse_expression())
            self.try_add(node, 'symbol', ')')
        # subroutineCall
        elif self.tokens[self.idx + 1] in (Token('symbol', '.'), Token('symbol', '(')): 
            node.append(self.parse_subroutine_call())
        # identifier | identifier '[' expression ']' 
        else:
            self.try_add(node, 'identifier')
            if self.token.value == '[':
                self.try_add(node, 'symbol', '[')
                node.append(self.parse_expression())
                self.try_add(node, 'symbol', ']')
        return node

    def parse_subroutine_call(self):
        """
        identifier '(' expressionList ')' | 
        identifier '.' identifier '(' expressionList ')'
        """
        node = Token('subroutineCall', [])
        self.try_add(node, 'identifier')
        if self.token.value == '.':
            self.try_add(node, 'identifier')
        self.try_add(node, 'symbol', '(')
        node.append(self.parse_expression_list())
        self.try_add(node, 'symbol', ')')
        return node

    def parse_expression_list(self):
        """
        (expression (',' expression)* )?
        We should always expect a trailing ')'
        """
        node = Token('expressionList')
        if self.token.value != ')':
            assert Token('symbol', ')') in self.tokens[self.idx:], 'Expression list must close'
            node.append(self.parse_expression())
            while self.token.value != ')':
                self.try_add(node, 'symbol', value=',')
                node.append(self.parse_expression)
        return node

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
        try:
            return self.tokens[self.idx]
        except IndexError:
            return Token(None, None)
