from unittest import TestCase
from mock import Mock, DEFAULT

from tokenizer import tokenize, Token
from jack_parser import Parser
from constants import KEYWORDS, SYMBOLS
from code_generator import CodeGenerator


class TestCodeGenerator(TestCase):
    maxDiff = None

    def test_compile_class(self):
        class_tree = Token('class', [
            Token('keyword', 'class'), 
            Token('identifier', 'Main'), 
            Token('symbol', '{'),
            Token('classVarDec', [
                Token('keyword', 'static'), 
                Token('keyword', 'int'),
                Token('identifier', 'foo'), 
                Token('symbol', ';'),
            ]),
            Token('classVarDec', [
                Token('keyword', 'field'), 
                Token('keyword', 'char'),
                Token('identifier', 'bar'), 
                Token('symbol', ','),
                Token('identifier', 'baz'), 
                Token('symbol', ';'),
            ]),
            Token('classVarDec', [
                Token('keyword', 'static'), 
                Token('keyword', 'boolean'),
                Token('identifier', 'bing'), 
                Token('symbol', ';'),
            ]),
            Token('subroutineDec', []),
            Token('subroutineDec', []),
            Token('symbol', '}'),
        ])

        generator = CodeGenerator()
        generator.compile_subroutine = Mock(return_value='')
        vm_code = generator.compile_class(class_tree)

        self.assertEqual(vm_code, '')
        self.assertEqual(generator.class_symbols, {
            'foo': {
                'type': 'int',
                'kind': 'static',
                'id': 0,
            },
            'bar': {
                'type': 'char',
                'kind': 'field',
                'id': 0,
            },
            'baz': {
                'type': 'char',
                'kind': 'field',
                'id': 1,
            },
            'bing': {
                'type': 'boolean',
                'kind': 'static',
                'id': 1,
            },
        })

    def test_compile_subroutine_constructor_0_fields(self):
        subroutine_tree = Token('subroutineDec', [
            Token('keyword', 'constructor'), 
            Token('keyword', 'Foo'),
            Token('identifier', 'new'), 
            Token('parameterList', [
                Token('keyword', 'int'),
                Token('identifier', 'foo'), 
            ]),
            Token('subroutineBody', [
                Token('statements', []),
            ]),
        ])

        generator = CodeGenerator()
        generator.compile_statements = Mock(return_value='')
        generator.class_symbols = {
            'foo': {
                'type': 'int',
                'kind': 'static',
                'id': 0,
            },
        }
        vm_code = generator.compile_subroutine(subroutine_tree)
        self.assertEqual(vm_code, (
            'push constant 0\n'
            'Memory.alloc 1\n'
            'pop pointer 0\n'
        ))

    def test_compile_subroutine_constructor_2_fields(self):
        subroutine_tree = Token('subroutineDec', [
            Token('keyword', 'constructor'), 
            Token('keyword', 'Foo'),
            Token('identifier', 'new'), 
            Token('parameterList', [
                Token('keyword', 'int'),
                Token('identifier', 'foo'), 
            ]),
            Token('subroutineBody', [
                Token('statements', []),
            ]),
        ])

        generator = CodeGenerator()
        generator.compile_statements = Mock(return_value='')
        generator.class_symbols = {
            'foo': {
                'type': 'int',
                'kind': 'static',
                'id': 0,
            },
            'bar': {
                'type': 'char',
                'kind': 'field',
                'id': 0,
            },
            'baz': {
                'type': 'char',
                'kind': 'field',
                'id': 1,
            },
        }
        vm_code = generator.compile_subroutine(subroutine_tree)
        self.assertEqual(vm_code, (
            'push constant 2\n'
            'Memory.alloc 1\n'
            'pop pointer 0\n'
        ))

    def test_compile_subroutine_function_with_vars(self):
        subroutine_tree = Token('subroutineDec', [
            Token('keyword', 'function'), 
            Token('keyword', 'int'),
            Token('identifier', 'foo'), 
            Token('parameterList', [
                Token('keyword', 'int'),
                Token('identifier', 'foo'), 
            ]),
            Token('subroutineBody', [
                Token('varDec', [
                    Token('keyword', 'var'),
                    Token('keyword', 'int'), 
                    Token('identifier', 'bar'), 
                    Token('symbol', ','),
                    Token('identifier', 'baz'), 
                    Token('symbol', ';')
                ]),
                Token('varDec', [
                    Token('keyword', 'var'),
                    Token('keyword', 'char'), 
                    Token('identifier', 'bing'), 
                    Token('symbol', ';')
                ]),
                Token('statements', []),
            ]),
        ])

        generator = CodeGenerator()
        generator.class_name = 'Foo'
        generator.compile_statements = Mock(return_value='')
        vm_code = generator.compile_subroutine(subroutine_tree)

        self.assertEqual(vm_code, '')
        self.assertEqual(generator.subroutine_symbols, {
            'foo': {
                'type': 'int',
                'kind': 'argument',
                'id': 0,
            },
            'bar': {
                'type': 'int',
                'kind': 'local',
                'id': 0,
            },
            'baz': {
                'type': 'int',
                'kind': 'local',
                'id': 1,
            },
            'bing': {
                'type': 'char',
                'kind': 'local',
                'id': 2,
            },
        })

    def test_compile_subroutine_method_with_args(self):
        subroutine_tree = Token('subroutineDec', [
            Token('keyword', 'method'), 
            Token('keyword', 'int'),
            Token('identifier', 'foo'), 
            Token('parameterList', [
                Token('keyword', 'int'),
                Token('identifier', 'bar'), 
                Token('symbol', ','), 
                Token('identifier', 'Array'),
                Token('identifier', 'baz'),
            ]),
            Token('subroutineBody', [
                Token('statements', []),
            ]),
        ])

        generator = CodeGenerator()
        generator.class_name = 'Foo'
        generator.compile_statements = Mock(return_value='')
        vm_code = generator.compile_subroutine(subroutine_tree)

        self.assertEqual(vm_code, (
            'push argument 0\n'
            'pop pointer 0\n'
        ))
        self.assertEqual(generator.subroutine_symbols, {
            'this': {
                'type': 'Foo',
                'kind': 'argument',
                'id': 0,
            },
            'bar': {
                'type': 'int',
                'kind': 'argument',
                'id': 1,
            },
            'baz': {
                'type': 'Array',
                'kind': 'argument',
                'id': 2,
            },
        })

    def test_compile_subroutine_method_no_args(self):
        subroutine_tree = Token('subroutineDec', [
            Token('keyword', 'method'), 
            Token('keyword', 'int'),
            Token('identifier', 'foo'), 
            Token('parameterList', []),
            Token('subroutineBody', [
                Token('statements', []),
            ]),
        ])

        generator = CodeGenerator()
        generator.class_name = 'Foo'
        generator.compile_statements = Mock(return_value='')
        vm_code = generator.compile_subroutine(subroutine_tree)

        self.assertEqual(vm_code, (
            'push argument 0\n'
            'pop pointer 0\n'
        ))
        self.assertEqual(generator.subroutine_symbols, {
            'this': {
                'type': 'Foo',
                'kind': 'argument',
                'id': 0,
            },
        })

    def test_compile_function_void_type(self):
        subroutine_tree = Token('subroutineDec', [
            Token('keyword', 'function'), 
            Token('keyword', 'void'),
            Token('identifier', 'foo'), 
            Token('parameterList', []),
            Token('subroutineBody', [
                Token('statements', [
                    Token('keyword', 'return'),
                ]),
            ]),
        ])

        generator = CodeGenerator()
        generator.class_name = 'Foo'
        generator.compile_statements = Mock(return_value='return\n')
        vm_code = generator.compile_subroutine(subroutine_tree)

        self.assertEqual(vm_code, (
            'push constant 0\n'
            'return\n'
        ))

    def test_compile_statements(self):
        pass

    def test_compile_let_statement(self):
        statement = Token('letStatement', [
            Token('keyword', 'let'),
            Token('identifier', 'foo'),
            Token('symbol', '='),
            Token('term', [Token('integerConstant', '1')]),
            Token('symbol', ';'),
        ])

        generator = CodeGenerator()
        generator.subroutine_symbols = {
            'foo': {
                'type': 'integerConstant',
                'kind': 'argument',
                'id': 1,
            },
        }
        vm_code = generator.compile_let(statement)
        self.assertEqual(vm_code, (
            'push constant 1\n'
            'pop argument 1\n'
        ))

    def test_compile_let_statement_array(self):
        statement = Token('letStatement', [
            Token('keyword', 'let'),
            Token('identifier', 'foo'),
            Token('identifier', '['),
            Token('term', [Token('integerConstant', '1')]),
            Token('identifier', ']'),
            Token('symbol', '='),
            Token('term', [Token('integerConstant', '2')]),
            Token('symbol', ';'),
        ])

        generator = CodeGenerator()
        generator.subroutine_symbols = {
            'foo': {
                'type': 'integerConstant',
                'kind': 'argument',
                'id': 1,
            },
        }
        vm_code = generator.compile_let(statement)
        self.assertEqual(vm_code, (
            'push argument 1\n'
            'push constant 1\n'
            'add\n'
            'push constant 2\n'
            'pop temp 0\n'
            'pop pointer 1\n'
            'push temp 0\n'
            'pop that 0\n'
        ))

    def test_compile_do_statement(self):
        # Class calling a function or constructor on a class
        statement = Token('doStatement', [
            Token('term', [
                Token('identifier', 'String'),
                Token('symbol', '.'),
                Token('identifier', 'getWord'),
                Token('symbol', '('),
                Token('expressionList', [
                    Token('term', [Token('integerConstant', '1')]),
                ]),
                Token('symbol', ')'),
            ])
        ])

        generator = CodeGenerator()
        generator.subroutine_symbols = {
            'this': {
                'type': 'BarClass',
                'kind': 'argument',
                'id': 0,
            },
        }
        vm_code = generator.compile_do(statement)
        self.assertEqual(vm_code, (
            'push constant 1\n'
            'call String.getWord 1\n'
            'pop temp 0\n'
        ))


    def test_compile_if_statement(self):
        pass

    def test_compile_while_statement(self):
        pass

    def test_compile_return_statement(self):
        pass

    def test_compile_expression_integer(self):
        term = Token('term', [
            Token('integerConstant', '2'), 
        ])

        generator = CodeGenerator()
        vm_code = generator.compile_expression(term)

        self.assertEqual(vm_code, (
            'push constant 2\n'
        ))

    def test_compile_expression_string(self):
        term = Token('term', [
            Token('stringConstant', 'hey ho.'), 
        ])
        generator = CodeGenerator()
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, (
            'push constant 7\n'
            'call String.new 1\n'
            'push temp 0\n'
            'pop temp 0\n'
            'push constant 104\n'
            'call String.appendChar 2\n'
            'pop temp 0\n'
            'push constant 101\n'
            'call String.appendChar 2\n'
            'pop temp 0\n'
            'push constant 121\n'
            'call String.appendChar 2\n'
            'pop temp 0\n'
            'push constant 32\n'
            'call String.appendChar 2\n'
            'pop temp 0\n'
            'push constant 104\n'
            'call String.appendChar 2\n'
            'pop temp 0\n'
            'push constant 111\n'
            'call String.appendChar 2\n'
            'pop temp 0\n'
            'push constant 46\n'
            'call String.appendChar 2\n'
            'pop temp 0\n'
        ))

    def test_compile_expression_identifier_class(self):
        term = Token('term', [
            Token('identifier', 'foo'), 
        ])
        generator = CodeGenerator()
        generator.class_symbols = {
            'foo': {
                'type': 'int',
                'kind': 'static',
                'id': 1,
            },
        }
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, (
            'push static 1\n'
        ))

    def test_compile_expression_identifier_subroutine(self):
        term = Token('term', [
            Token('identifier', 'foo'), 
        ])
        generator = CodeGenerator()
        generator.subroutine_symbols = {
            'foo': {
                'type': 'int',
                'kind': 'argument',
                'id': 2,
            }
        }
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, (
            'push argument 2\n'
        ))

    def test_compile_expression_keyword_const(self):
        generator = CodeGenerator()
        generator.subroutine_symbols = {
            'this': {
                'type': 'Foo',
                'kind': 'argument',
                'id': 0,
            }
        }
        # this
        term = Token('term', [Token('keyword', 'this')])
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, ('push argument 0\n'))

        # false
        term = Token('term', [Token('keyword', 'false')])
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, ('push constant 0\n'))

        # null
        term = Token('term', [Token('keyword', 'null')])
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, ('push constant 0\n'))

        # true
        term = Token('term', [Token('keyword', 'true')])
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, ('push constant 1\nneg\n'))

    def test_compile_expression_parens(self):
        term = Token('term', [
            Token('symbol', '('), 
            Token('term', [
                Token('integerConstant', '2'), 
            ]),
            Token('symbol', ')'), 
        ])

        generator = CodeGenerator()
        vm_code = generator.compile_expression(term)

        self.assertEqual(vm_code, (
            'push constant 2\n'
        ))

    def test_compile_expression_unary_ops(self):
        generator = CodeGenerator()
        generator.subroutine_symbols = {
            'foo': {
                'type': 'int',
                'kind': 'argument',
                'id': 0,
            }
        }
        # not
        term = Token('term', [
            Token('symbol', '~'), 
            Token('term', [Token('identifier', 'foo')])
        ])
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, (
            'push argument 0\n'
            'not\n'
        ))
        # neg
        term = Token('term', [
            Token('symbol', '-'), 
            Token('term', [Token('identifier', 'foo')])
        ])
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, (
            'push argument 0\n'
            'neg\n'
        ))

    def test_compile_expression_expression_with_op(self):
        term = Token('expression', [
            Token('term', [Token('integerConstant', '1')]),
            Token('symbol', '+'),
            Token('term', [Token('integerConstant', '2')]),
        ])

        generator = CodeGenerator()
        vm_code = generator.compile_expression(term)

        self.assertEqual(vm_code, (
            'push constant 1\n'
            'push constant 2\n'
            'add\n'
        ))

    def test_compile_expression_expression_with_term(self):
        term = Token('expression', [
            Token('term', [Token('integerConstant', '1')]),
        ])

        generator = CodeGenerator()
        vm_code = generator.compile_expression(term)

        self.assertEqual(vm_code, (
            'push constant 1\n'
        ))

    def test_compile_expression_array_access(self):
        term = Token('term', [
            Token('identifier', 'foo'),
            Token('symbol', '['),
            Token('expression', [
                Token('term', [Token('integerConstant', '12')]),
            ]),
            Token('symbol', ']'),
        ])

        generator = CodeGenerator()
        generator.subroutine_symbols = {
            'foo': {
                'type': 'Array',
                'kind': 'local',
                'id': 0,
            }
        }
        vm_code = generator.compile_expression(term)

        self.assertEqual(vm_code, (
            'push constant 12\n'
            'push local 0\n'
            'add\n'
            'pop pointer 1\n'
            'push that 0\n'
        ))

    def test_compile_expression_method_self(self):
        # Class calling a method on itself
        term = Token('term', [
            Token('identifier', 'bar_method'),
            Token('symbol', '('),
            Token('expressionList', [
                Token('term', [Token('integerConstant', '1')]),
                Token('symbol', ','),
                Token('term', [Token('integerConstant', '2')]),
                Token('symbol', ','),
                Token('term', [Token('integerConstant', '3')]),
            ]),
            Token('symbol', ')'),
        ])

        generator = CodeGenerator()
        generator.subroutine_symbols = {
            'this': {
                'type': 'BarClass',
                'kind': 'argument',
                'id': 0,
            }
        }
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, (
            'push argument 0\n'
            'push constant 1\n'
            'push constant 2\n'
            'push constant 3\n'
            'call BarClass.bar_method 4\n'
        ))
    
    def test_compile_expression_call_subroutine_var(self):
        # Class calling a method on another class
        term = Token('term', [
            Token('identifier', 'foo_instance'),
            Token('symbol', '.'),
            Token('identifier', 'foo_method'),
            Token('symbol', '('),
            Token('expressionList', [
                Token('term', [Token('integerConstant', '1')]),
                Token('symbol', ','),
                Token('term', [Token('integerConstant', '2')]),
            ]),
            Token('symbol', ')'),
        ])

        generator = CodeGenerator()
        generator.subroutine_symbols = {
            'this': {
                'type': 'BarClass',
                'kind': 'argument',
                'id': 0,
            },
            'foo_instance': {
                'type': 'FooClass',
                'kind': 'local',
                'id': 7,
            }
        }
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, (
            'push local 7\n'
            'push constant 1\n'
            'push constant 2\n'
            'call FooClass.foo_method 3\n'
        ))

    def test_compile_expression_call_subroutine_other(self):
        # Class calling a function or constructor on a class
        term = Token('term', [
            Token('identifier', 'String'),
            Token('symbol', '.'),
            Token('identifier', 'getWord'),
            Token('symbol', '('),
            Token('expressionList', [
                Token('term', [Token('integerConstant', '1')]),
            ]),
            Token('symbol', ')'),
        ])

        generator = CodeGenerator()
        generator.subroutine_symbols = {
            'this': {
                'type': 'BarClass',
                'kind': 'argument',
                'id': 0,
            },
        }
        vm_code = generator.compile_expression(term)
        self.assertEqual(vm_code, (
            'push constant 1\n'
            'call String.getWord 1\n'
        ))

    def test_compile_expression_list_many(self):
        expression_List = Token('expressionList', [
            Token('expression', [
                Token('term', [Token('integerConstant', '1')]),
            ]),
            Token('symbol', ','),
            Token('expression', [
                Token('term', [Token('integerConstant', '2')]),
            ]),
            Token('symbol', ','),
            Token('expression', [
                Token('term', [Token('integerConstant', '3')]),
            ]),
        ])
        generator = CodeGenerator()
        vm_code = generator.compile_expression_list(expression_List)

        self.assertEqual(vm_code, (
            'push constant 1\n'
            'push constant 2\n'
            'push constant 3\n'
        ))

    def test_compile_expression_list_one(self):
        expression_List = Token('expressionList', [
            Token('expression', [
                Token('term', [Token('integerConstant', '1')]),
            ])
        ])
        generator = CodeGenerator()
        vm_code = generator.compile_expression_list(expression_List)

        self.assertEqual(vm_code, (
            'push constant 1\n'
        ))

    def test_compile_expression_list_none(self):
        expression_List = Token('expressionList', [])
        generator = CodeGenerator()
        vm_code = generator.compile_expression_list(expression_List)
        self.assertEqual(vm_code, '')


class TestParser(TestCase):

    @staticmethod
    def _progress_parse(instance):
        instance.idx += 1
        return DEFAULT

    @staticmethod
    def _mock_parse(instance, iterable=False):
        if iterable:
            return Mock(
            return_value=[Token('dummy', 'dummy')],
            side_effect=lambda: TestParser._progress_parse(instance)
        )
        else:
            return Mock(
            return_value=Token('dummy', 'dummy'),
            side_effect=lambda: TestParser._progress_parse(instance)
        ) 

    def test_class_no_body(self):
        """
        'class' className '{' classVarDec* subroutineDec* '}' 
        """
        tokens = (
            Token('keyword', 'class'), 
            Token('identifier', 'Main'), 
            Token('symbol', '{'),
            Token('symbol', '}'),
        )

        expected = Token('class', [
                Token('keyword', 'class'), 
                Token('identifier', 'Main'), 
                Token('symbol', '{'),
                Token('symbol', '}'),
        ])

        actual = Parser(tokens).parse_class()
        self.assertEqual(expected, actual)

    def test_class_with_body(self):
        """
        'class' className '{' classVarDec* subroutineDec* '}' 
        """
        tokens = (
            Token('keyword', 'class'), 
            Token('identifier', 'Main'), 
            Token('symbol', '{'),
            Token('keyword', 'static'),  # Dummy class var declaration
            Token('keyword', 'function'),  # Dummy subroutine declaration
            Token('symbol', '}'),
        )

        expected = Token('class', [
            Token('keyword', 'class'), 
            Token('identifier', 'Main'), 
            Token('symbol', '{'),
            Token('dummy', 'dummy'),
            Token('dummy', 'dummy'),
            Token('symbol', '}'),
        ])

        parser = Parser(tokens)
        parser.parse_class_var_declaration = self._mock_parse(parser)
        parser.parse_subroutine_declaration = self._mock_parse(parser)

        actual = parser.parse_class()
        self.assertEqual(expected, actual)

    def test_class_var_declaration(self):
        """
        ('static' | 'field' ) type varName (',' varName)* ';' 
        """
        tokens = (
            Token('keyword', 'static'), 
            Token('keyword', 'int'),  # Dummy type
            Token('identifier', 'foo'), 
            Token('symbol', ';'),
        )

        expected = Token('classVarDec', [
            Token('keyword', 'static'), 
            Token('dummy', 'dummy'),
            Token('identifier', 'foo'), 
            Token('symbol', ';'),
        ])

        parser = Parser(tokens)
        parser.parse_type = self._mock_parse(parser)

        actual = parser.parse_class_var_declaration()
        self.assertEqual(expected, actual)

    def test_class_var_declaration_multiple(self):
        """
        ('static' | 'field' ) type varName (',' varName)* ';' 
        """
        tokens = (
            Token('keyword', 'static'), 
            Token('keyword', 'int'),  # Dummy type
            Token('identifier', 'foo'), 
            Token('symbol', ','),
            Token('identifier', 'bar'), 
            Token('symbol', ','),
            Token('identifier', 'baz'), 
            Token('symbol', ';'),
        )

        expected = Token('classVarDec', [
            Token('keyword', 'static'), 
            Token('dummy', 'dummy'),
            Token('identifier', 'foo'), 
            Token('symbol', ','),
            Token('identifier', 'bar'), 
            Token('symbol', ','),
            Token('identifier', 'baz'), 
            Token('symbol', ';'),  
        ])

        parser = Parser(tokens)
        parser.parse_type = self._mock_parse(parser)

        actual = parser.parse_class_var_declaration()
        self.assertEqual(expected, actual)

    def test_parse_subroutine_declaration(self):
        """
        ('constructor'|'function'|'method')  ('void'|type) identifier '('parameterList ')' subroutineBody
        """
        tokens = (
            Token('keyword', 'method'), 
            Token('keyword', 'int'),  # Dummy type
            Token('identifier', 'foo'), 
            Token('symbol', '('),
            Token('dummy', 'dummy'),  # Dummy parameterList 
            Token('symbol', ')'),
            Token('dummy', 'dummy'), # Dummy subroutineBody
        )

        expected = Token('subroutineDec', [
            Token('keyword', 'method'), 
            Token('dummy', 'dummy'),  # Dummy type
            Token('identifier', 'foo'), 
            Token('symbol', '('),
            Token('dummy', 'dummy'),  # Dummy parameterList 
            Token('symbol', ')'),
            Token('dummy', 'dummy'), # Dummy subroutineBody
        ])

        parser = Parser(tokens)
        parser.parse_type = self._mock_parse(parser)
        parser.parse_parameter_list = self._mock_parse(parser)
        parser.parse_subroutine_body = self._mock_parse(parser)

        actual = parser.parse_subroutine_declaration()
        self.assertEqual(expected, actual)


    def test_parse_subroutine_body(self):
        """
        '{' varDec* statements '}' 
        """
        tokens = (
            Token('symbol', '{'), 
            Token('keyword', 'var'),  # Dummy var dec
            Token('keyword', 'var'),  # Dummy var dec
            Token('dummy', 'dummy'),  # Dummy statements 
            Token('symbol', '}'),
        )

        expected = Token('subroutineBody', [
            Token('symbol', '{'), 
            Token('dummy', 'dummy'),  # Dummy var dec
            Token('dummy', 'dummy'),  # Dummy var dec
            Token('dummy', 'dummy'),  # Dummy statements 
            Token('symbol', '}'),
        ])

        parser = Parser(tokens)
        parser.parse_var_declaration = self._mock_parse(parser)
        parser.parse_statements = self._mock_parse(parser)
        
        actual = parser.parse_subroutine_body()
        self.assertEqual(expected, actual)


    def test_parse_var_declaration(self):
        """
        'var' type varName (',' varName)* ';'
        """
        tokens = (
            Token('keyword', 'var'),
            Token('dummy', 'dummy'),  # Dummy type 
            Token('identifier', 'foo'),
            Token('symbol', ','),
            Token('identifier', 'bar'), 
            Token('symbol', ';'),
        )

        expected = Token('varDec', [
            Token('keyword', 'var'),
            Token('dummy', 'dummy'),  # Dummy type 
            Token('identifier', 'foo'),
            Token('symbol', ','),
            Token('identifier', 'bar'), 
            Token('symbol', ';'),
        ])

        parser = Parser(tokens)
        parser.parse_type = self._mock_parse(parser)
        
        actual = parser.parse_var_declaration()
        self.assertEqual(expected, actual)

    def test_parse_parameter_list(self):
        """
        ( (type identifier) (',' type identifier)*)?
        """
        tokens = (
            Token('dummy', 'dummy'),  # Dummy type 
            Token('identifier', 'foo'),
            Token('symbol', ','),
            Token('dummy', 'dummy'),  # Dummy type 
            Token('identifier', 'bar'), 
        )

        expected = Token('parameterList', [
            Token('dummy', 'dummy'),  # Dummy type 
            Token('identifier', 'foo'),
            Token('symbol', ','),
            Token('dummy', 'dummy'),  # Dummy type 
            Token('identifier', 'bar'), 
        ])

        parser = Parser(tokens)
        parser.parse_type = self._mock_parse(parser)
        
        actual = parser.parse_parameter_list()
        self.assertEqual(expected, actual)


    def test_parse_parameter_list_empty(self):
        """
        ( (type identifier) (',' type identifier)*)?
        """
        tokens = (Token('symbol',')'), )
        expected = Token('parameterList', [])

        parser = Parser(tokens)
        parser.parse_type = self._mock_parse(parser)
        
        actual = parser.parse_parameter_list()
        self.assertEqual(expected, actual)


    def test_parse_statements(self):
        """
        (letStatement | ifStatement | whileStatement | doStatement | returnStatement)*
        """
        tokens = (
            Token('keyword', 'let'), 
            Token('keyword', 'if'),
            Token('keyword', 'while'),
            Token('keyword', 'do'),   
            Token('keyword', 'return'), 
            Token('symbol', '}')  # Expect unparsed
        )

        expected = Token('statements', [
            Token('dummy', 'dummy'), 
            Token('dummy', 'dummy'), 
            Token('dummy', 'dummy'), 
            Token('dummy', 'dummy'), 
            Token('dummy', 'dummy'), 
        ])

        parser = Parser(tokens)

        parser.parse_let_statement = self._mock_parse(parser)
        parser.parse_if_statement = self._mock_parse(parser)
        parser.parse_while_statement = self._mock_parse(parser)
        parser.parse_do_statement = self._mock_parse(parser)
        parser.parse_return_statement = self._mock_parse(parser)
        
        actual = parser.parse_statements()
        self.assertEqual(expected, actual)


    def test_parse_let_statement(self):
        """
        'let' varName ('[' expression ']')? '=' expression ';'
        """
        tokens = (
            Token('keyword', 'let'), 
            Token('identifier', 'foo'),
            Token('symbol', '='),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ';'), 
        )

        expected = Token('letStatement', [
            Token('keyword', 'let'), 
            Token('identifier', 'foo'),
            Token('symbol', '='),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ';'), 
        ])

        parser = Parser(tokens)
        parser.parse_expression = self._mock_parse(parser)
        actual = parser.parse_let_statement()
        self.assertEqual(expected, actual)

    def test_parse_let_statement_index(self):
        """
        'let' varName ('[' expression ']')? '=' expression ';'
        """
        tokens = (
            Token('keyword', 'let'), 
            Token('identifier', 'foo'),
            Token('symbol', '['),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ']'),
            Token('symbol', '='),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ';'), 
        )

        expected = Token('letStatement', [
            Token('keyword', 'let'), 
            Token('identifier', 'foo'),
            Token('symbol', '['),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ']'),
            Token('symbol', '='),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ';'), 
        ])

        parser = Parser(tokens)
        parser.parse_expression = self._mock_parse(parser)
        actual = parser.parse_let_statement()
        self.assertEqual(expected, actual)

    def test_parse_if_statement(self):
        """
        'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?
        """
        tokens = (
            Token('keyword', 'if'), 
            Token('symbol', '('),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', '}'), 
        )

        expected = Token('ifStatement', [
            Token('keyword', 'if'), 
            Token('symbol', '('),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('dummy', 'dummy'),  # Dummy statements   
            Token('symbol', '}'), 
        ])

        parser = Parser(tokens)
        parser.parse_expression = self._mock_parse(parser)
        parser.parse_statements = self._mock_parse(parser)
        actual = parser.parse_if_statement()
        self.assertEqual(expected, actual)

    def test_parse_if_else_statement(self):
        """
        'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?
        """
        tokens = (
            Token('keyword', 'if'), 
            Token('symbol', '('),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('dummy', 'dummy'),  # Dummy statements   
            Token('symbol', '}'),
            Token('keyword', 'else'), 
            Token('symbol', '{'),
            Token('dummy', 'dummy'),  # Dummy statements   
            Token('symbol', '}'),
        )

        expected = Token('ifStatement', [
            Token('keyword', 'if'), 
            Token('symbol', '('),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('dummy', 'dummy'),  # Dummy statements   
            Token('symbol', '}'),
            Token('keyword', 'else'), 
            Token('symbol', '{'),
            Token('dummy', 'dummy'),  # Dummy statements   
            Token('symbol', '}'), 
        ])

        parser = Parser(tokens)
        parser.parse_expression = self._mock_parse(parser)
        parser.parse_statements = self._mock_parse(parser)
        actual = parser.parse_if_statement()
        self.assertEqual(expected, actual)

    def test_parse_while_statement(self):
        """
        'while' '(' expression ')' '{' statements '}'
        """
        tokens = (
            Token('keyword', 'while'), 
            Token('symbol', '('),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', '}'), 
        )

        expected = Token('whileStatement', [
            Token('keyword', 'while'), 
            Token('symbol', '('),
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('dummy', 'dummy'),  # Dummy statements   
            Token('symbol', '}'), 
        ])

        parser = Parser(tokens)
        parser.parse_expression = self._mock_parse(parser)
        parser.parse_statements = self._mock_parse(parser)
        actual = parser.parse_while_statement()
        self.assertEqual(expected, actual)


    def test_parse_do_statement(self):
        """
        'do' subroutineCall ';'
        """
        tokens = (
            Token('keyword', 'do'), 
            Token('dummy', 'dummy'),  # Dummy subroutineCall   
            Token('symbol', ';'), 
        )

        expected = Token('doStatement', [
            Token('keyword', 'do'), 
            Token('dummy', 'dummy'),  # Dummy subroutineCall   
            Token('symbol', ';'), 
        ])

        parser = Parser(tokens)
        parser.parse_subroutine_call = self._mock_parse(parser, iterable=True)
        actual = parser.parse_do_statement()
        self.assertEqual(expected, actual)

    def test_parse_return_statement(self):
        """
        'return' expression? ';' 
        """
        tokens = (
            Token('keyword', 'return'), 
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ';'), 
        )

        expected = Token('returnStatement', [
            Token('keyword', 'return'), 
            Token('dummy', 'dummy'),  # Dummy expression   
            Token('symbol', ';'), 
        ])

        parser = Parser(tokens)
        parser.parse_expression = self._mock_parse(parser)
        actual = parser.parse_return_statement()
        self.assertEqual(expected, actual)

    def test_parse_return_statement_empty(self):
        """
        'return' expression? ';' 
        """
        tokens = (
            Token('keyword', 'return'), 
            Token('symbol', ';'), 
        )

        expected = Token('returnStatement', [
            Token('keyword', 'return'), 
            Token('symbol', ';'), 
        ])

        parser = Parser(tokens)
        actual = parser.parse_return_statement()
        self.assertEqual(expected, actual)

    def test_parse_expression(self):
        """
        term (op term)*
        """
        tokens = (
            Token('integerConstant', '1'), 
            Token('symbol', '+'), 
            Token('integerConstant', '1'), 
            Token('symbol', '+'),
            Token('integerConstant', '1'), 
        )

        expected = Token('expression', [
            Token('dummy', 'dummy'), 
            Token('symbol', '+'), 
            Token('dummy', 'dummy'), 
            Token('symbol', '+'),
            Token('dummy', 'dummy'),  
        ])

        parser = Parser(tokens)
        parser.parse_term = self._mock_parse(parser)
        actual = parser.parse_expression()
        self.assertEqual(expected, actual)

    def test_parse_term(self):
        """
        integerConstant | stringConstant | keywordConstant | 
        identifier | identifier '[' expression ']' | 
        subroutineCall | '(' expression ')' | (unaryOp term)
        """
        pass 

    def test_parse_subroutine_call(self):
        """
        identifier '(' expressionList ')' | 
        identifier '.' identifier '(' expressionList ')'
        """
        pass

    def test_parse_expression_list(self):
        """
        (expression (',' expression)* )? 
        """
        pass


class TestTokenizer(TestCase):
    maxDiff = None
    def test_tokenize(self):
        jack_text = """
        class Main {
            static boolean test;    // Added for testing -- there is no static keyword
                                    // in the Square files.
            function void main() {
              var SquareGame game;
              let game = SquareGame.new();
              do game.run();
              do game.dispose();
              return;
            }

            function void test() {  // Added to test Jack syntax that is not use in
                var int i, j;       // the Square files.
                var String s;
                var Array a;
                if (false) {
                    let s = "string constant";
                    let s = null;
                    let a[1] = a[2];
                }
                else {              // There is no else keyword in the Square files.
                    let i = i * (-j);
                    let j = j / (-2);   // note: unary negate constant 2
                    let i = i | j;
                }
                return;
            }
        }
        """
        actual = tokenize(jack_text)
        expected = [
            Token('keyword', 'class'), 
            Token('identifier', 'Main'), 
            Token('symbol', '{'),
            Token('keyword', 'static'),
            Token('keyword', 'boolean'),
            Token('identifier', 'test'),
            Token('symbol', ';'),
            Token('keyword', 'function'),
            Token('keyword', 'void'),
            Token('identifier', 'main'),
            Token('symbol', '('),
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('keyword', 'var'),
            Token('identifier', 'SquareGame'),
            Token('identifier', 'game'),
            Token('symbol', ';'),
            Token('keyword', 'let'),
            Token('identifier', 'game'),
            Token('symbol', '='),
            Token('identifier', 'SquareGame'),
            Token('symbol', '.'),
            Token('identifier', 'new'),
            Token('symbol', '('),
            Token('symbol', ')'),
            Token('symbol', ';'),
            Token('keyword', 'do'),
            Token('identifier', 'game'),
            Token('symbol', '.'),
            Token('identifier', 'run'),
            Token('symbol', '('),
            Token('symbol', ')'),
            Token('symbol', ';'),
            Token('keyword', 'do'),
            Token('identifier', 'game'),
            Token('symbol', '.'),
            Token('identifier', 'dispose'),
            Token('symbol', '('),
            Token('symbol', ')'),
            Token('symbol', ';'),
            Token('keyword', 'return'),
            Token('symbol', ';'),
            Token('symbol', '}'),
            Token('keyword', 'function'),
            Token('keyword', 'void'),
            Token('identifier', 'test'),
            Token('symbol', '('),
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('keyword', 'var'),
            Token('keyword', 'int'),
            Token('identifier', 'i'),
            Token('symbol', ','),
            Token('identifier', 'j'),
            Token('symbol', ';'),
            Token('keyword', 'var'),
            Token('identifier', 'String'),
            Token('identifier', 's'),
            Token('symbol', ';'),
            Token('keyword', 'var'),
            Token('identifier', 'Array'),
            Token('identifier', 'a'),
            Token('symbol', ';'),
            Token('keyword', 'if'),
            Token('symbol', '('),
            Token('keyword', 'false'),
            Token('symbol', ')'),
            Token('symbol', '{'),
            Token('keyword', 'let'),
            Token('identifier', 's'),
            Token('symbol', '='),
            Token('stringConstant', 'string constant'),
            Token('symbol', ';'),
            Token('keyword', 'let'),
            Token('identifier', 's'),
            Token('symbol', '='),
            Token('keyword', 'null'),
            Token('symbol', ';'),
            Token('keyword', 'let'),
            Token('identifier', 'a'),
            Token('symbol', '['),
            Token('integerConstant', '1'),
            Token('symbol', ']'),
            Token('symbol', '='),
            Token('identifier', 'a'),
            Token('symbol', '['),
            Token('integerConstant', '2'),
            Token('symbol', ']'),
            Token('symbol', ';'),
            Token('symbol', '}'),
            Token('keyword', 'else'),
            Token('symbol', '{'),
            Token('keyword', 'let'),
            Token('identifier', 'i'),
            Token('symbol', '='),
            Token('identifier', 'i'),
            Token('symbol', '*'),
            Token('symbol', '('),
            Token('symbol', '-'),
            Token('identifier', 'j'),
            Token('symbol', ')'),
            Token('symbol', ';'),
            Token('keyword', 'let'),
            Token('identifier', 'j'),
            Token('symbol', '='),
            Token('identifier', 'j'),
            Token('symbol', '/'),
            Token('symbol', '('),
            Token('symbol', '-'),
            Token('integerConstant', '2'),
            Token('symbol', ')'),
            Token('symbol', ';'),
            Token('keyword', 'let'),
            Token('identifier', 'i'),
            Token('symbol', '='),
            Token('identifier', 'i'),
            Token('symbol', '|'),
            Token('identifier', 'j'),
            Token('symbol', ';'),
            Token('symbol', '}'),
            Token('keyword', 'return'),
            Token('symbol', ';'),
            Token('symbol', '}'),
            Token('symbol', '}'),
        ]
        self.assertEqual(expected, actual)

    def test_symbol(self):
        for symbol in SYMBOLS:
            tokens = tokenize(symbol)
            expected = Token('symbol', symbol)
            self.assertEqual(expected, tokens[0])

    def test_keyword(self):
        for keyword in KEYWORDS:
            tokens = tokenize(keyword)
            expected = Token('keyword', keyword)
            self.assertEqual(expected, tokens[0])

    def test_string(self):
        jack_text = 'let foo = "this is a string";'
        tokens = tokenize(jack_text)
        expected = Token('stringConstant', 'this is a string')
        self.assertEqual(expected, tokens[3])

    def test_int(self):
        jack_text = 'let foo = 1234'
        tokens = tokenize(jack_text)
        expected = Token('integerConstant', '1234')
        self.assertEqual(expected, tokens[3])