"""
Compiles a parse tree into Jack VM instructions
"""

# TODO: Add debug logging

class CodeGenerator(object):
    def __init__(self):
        self.class_symbols = {}
        self.subroutine_symbols = {}
        self.label_count = 0
        self.class_name = None

    def compile_class(self, parse_tree):
        assert parse_tree.has_children
        assert parse_tree[1].type == 'identifier'
        self.class_name = parse_tree[1].value
        print 'Parsing class {}'.format(self.class_name)

        var_counts = {
            'static': 0,
            'field': 0
        }

        class_var_decs = (t for t in parse_tree if t.type == 'classVarDec')
        for class_var_dec in class_var_decs:
            var_kind = class_var_dec[0].value
            var_type = class_var_dec[1].value
            
            for token in class_var_dec[2:]:
                if token.value in (',', ';'):
                    continue
                var_name = token.value
                self.class_symbols[var_name] = {
                    'type': var_type,
                    'kind': var_kind,
                    'id': var_counts[var_kind],
                }
                var_counts[var_kind] += 1

        subroutine_decs = (t for t in parse_tree if t.type == 'subroutineDec')
        return ''.join([self.compile_subroutine(dec) for dec in subroutine_decs])

    def compile_subroutine(self, parse_tree):
        assert parse_tree.type == 'subroutineDec'
        subroutine_type = parse_tree[0].value
        is_void = parse_tree[1].value == 'void'
        subroutine_name = parse_tree[2].value
        print 'Parsing {}.{}'.format(self.class_name, subroutine_name)

        parameter_list = next(t for t in parse_tree if t.type == 'parameterList')
        body = next(t for t in parse_tree if t.type == 'subroutineBody')
        var_decs = (t for t in body if t.type == 'varDec')
        statements = next(t for t in body if t.type == 'statements')

        self.subroutine_symbols = {}

        # Subroutine arguments
        arg_count = 0
        if subroutine_type == 'method':
            self.subroutine_symbols['this'] = {
                'type': self.class_name,
                'kind': 'argument',
                'id': arg_count / 2,
            }
            arg_count += 2

        arg_type = None
        for t in parameter_list:
            if t.value == ',':
                continue
            if arg_count % 2 == 0:
                arg_type = t.value
            else:
                arg_name = t.value
                self.subroutine_symbols[arg_name] = {
                    'type': arg_type,
                    'kind': 'argument',
                    'id': arg_count / 2,
                }
            arg_count += 1


        # Subroutine variable declarations
        var_count = 0
        for var_dec in var_decs:
            var_type = var_dec[1].value
            for token in var_dec[2:]:
                if token.value in (',', ';'):
                    continue
                var_name = token.value
                self.subroutine_symbols[var_name] = {
                    'type': var_type,
                    'kind': 'local',
                    'id': var_count,
                }
                var_count += 1


        # Handle object pointer
        if subroutine_type == 'constructor':
            num_fields = sum(
                1 for var in self.class_symbols.values()
                if var['kind'] == 'field'
            )
            obj_pointer_cmds = (
                'push constant {}\n'    # Push number of arguments
                'Memory.alloc 1\n'      # Allocate memory for object
                'pop pointer 0\n'       # Set THIS as allocated memory block
            ).format(num_fields)
        elif subroutine_type == 'method':
            obj_pointer_cmds = (
                'push argument 0\n'     # Push 1st arg (this)
                'pop pointer 0\n'       # Set THIS to current object
            )
        else:
            obj_pointer_cmds = ''

        statements_cmds = self.compile_statements(statements)

        # Handle void return value
        if is_void:
            statements_cmds = statements_cmds.replace(
                'return\n',
                'push constant 0\nreturn\n'
            )

        # Make sure we handle void return types here later
        return obj_pointer_cmds + statements_cmds

    def compile_statements(self, statements):
        lookup = {
            'letStatement': lambda x: self.compile_let(x),
            'doStatement': lambda x: self.compile_do(x),
            'ifStatement': lambda x: self.compile_if(x),
            'whileStatement': lambda x: self.compile_while(x),
            'returnStatement': lambda x: self.compile_return(x)
        }
        return ''.join([
            lookup[s.type](s) for s in statements
        ])

    def compile_let(self, parse_tree):
        # 'let' varName ('[' expression ']')? '=' expression ';'
        assert parse_tree.type == 'letStatement'
        assert parse_tree[0].value == 'let'
        var = self._get_variable(parse_tree[1].value)
        if parse_tree[2].value == '[':
            indexExp = self.compile_expression(parse_tree[3])
            valueExp = self.compile_expression(parse_tree[6])
            return (
                'push {kind} {id}\n'
                '{indexExp}'
                'add\n'
                '{valueExp}'
                'pop temp 0\n'
                'pop pointer 1\n'
                'push temp 0\n'
                'pop that 0\n'
            ).format(indexExp=indexExp, valueExp=valueExp, **var)
        else:
            valueExp = self.compile_expression(parse_tree[3])
            return valueExp + (
                'pop {kind} {id}\n'
            ).format(**var)

    def compile_do(self, parse_tree):
        assert parse_tree.type == 'doStatement'
        return self.compile_expression(parse_tree.value[0]) + (
            'pop temp 0\n'  # Clear return value
        )
 
    def compile_if(self, parse_tree):
        # 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )? 
        assert parse_tree.type == 'ifStatement'
        assert len(parse_tree) in (7, 11)
        expression = self.compile_expression(parse_tree[2])
        if_statements = self.compile_statements(parse_tree[5])
        if len(parse_tree) == 11:
            else_statements = self.compile_statements(parse_tree[9])
        else:
            else_statements = ''
        return (
            '{exp}'
            'if-goto {if_label}\n'
            'goto {else_label}\n'
            'label {if_label}\n'
            '{if_statements}'
            'goto {end_label}\n'
            'label {else_label}\n'
            '{else_statements}'
            'label {end_label}\n'
        ).format(
            exp=expression,
            if_statements=if_statements,
            else_statements=else_statements,
            if_label=self._get_label(),
            else_label=self._get_label(),
            end_label=self._get_label(),
        )

    def compile_while(self, parse_tree):
        # 'while' '(' expression ')' '{' statements '}' 
        assert parse_tree.type == 'whileStatement'
        assert len(parse_tree) == 7
        expression = self.compile_expression(parse_tree[2])
        statements = self.compile_statements(parse_tree[5])
        return (
            'label {loop_label}\n'
            '{exp}'
            'neg\n'
            'if-goto {end_label}\n'
            '{statements}'
            'goto {loop_label}\n'
            'label {end_label}\n'
        ).format(
            exp=expression,
            statements=statements,
            loop_label=self._get_label(),
            end_label=self._get_label(),
        )

    def compile_return(self, parse_tree):
        # return expression? ;
        # compile_subroutine handles void methods, just 'return' when no value specified
        assert parse_tree.type == 'returnStatement'
        if parse_tree[1].type in ('expression', 'term'):
            return_val = self.compile_expression(parse_tree[1])
        else:
            return_val = ''
        return '{}return\n'.format(return_val)

    def compile_expression(self, parse_tree):
        assert parse_tree.type in ('expression', 'term')

        if parse_tree.type == 'term':
            terms = parse_tree.value
            if terms[0].type == 'integerConstant':
                # Numbers
                assert len(terms) == 1
                return 'push constant {}\n'.format(terms[0].value)
            elif terms[0].type == 'stringConstant':
                # Strings
                assert len(terms) == 1
                string = terms[0].value
                return (
                    # Create a new string obj, reserve THIS in temp
                    'push constant {}\n'
                    'call String.new 1\n'
                    'push temp 0\n'
                ).format(len(string)) + ''.join([
                    (
                        # Append each character to the string
                        'pop temp 0\n'
                        'push constant {}\n'
                        'call String.appendChar 2\n'
                    ).format(ord(c)) for c in string 
                ]) + (
                    'pop temp 0\n'
                )
            elif terms[0].type == 'keyword':
                # Keyword constants 'true' | 'false' | 'null' | 'this' 
                assert len(terms) == 1
                keyword = terms[0].value
                if keyword == 'this':
                    variable = self._get_variable(keyword)
                    return 'push {kind} {id}\n'.format(**variable)
                elif keyword in ('null', 'false'):
                    return 'push constant 0\n'
                elif keyword == 'true':
                    return 'push constant 1\nneg\n'
                else:
                    raise ValueError('{} is not a valid keyword'.format(terms[0]))
            elif len(terms) > 3 and terms[0].type == 'identifier' and  terms[1].value == '[':
                # Array access varName [ ex ]
                assert terms[2].type == 'expression'
                variable = self._get_variable(terms[0].value)
                return self.compile_expression(terms[2]) + (
                    'push {kind} {id}\n'
                    'add\n'
                    'pop pointer 1\n'
                    'push that 0\n'
                ).format(**variable)
               
            elif (
                len(terms) > 3 and (
                    (terms[0].type == 'identifier' and terms[1].value == '.') or
                    (terms[0].type == 'identifier' and terms[1].value == '(')
                )
            ):
                return self.compile_subroutine_call(terms)
            elif terms[0].value == '(' and terms[-1].value == ')':
                # ( expression )
                assert len(terms) == 3
                return self.compile_expression(terms[1])
            elif terms[0].type == 'symbol':
                # Unary operations (-, ~)
                assert len(terms) == 2
                return self.compile_expression(terms[1]) + self.compile_unary_op(terms[0]) 
            elif terms[0].type == 'identifier':
                # Variables
                assert len(terms) == 1
                variable = self._get_variable(terms[0].value)
                return 'push {kind} {id}\n'.format(**variable)
            else:
                raise ValueError('{} is not a valid term'.format(parse_tree))
        elif parse_tree.type == 'expression':
            if len(parse_tree.value) == 1:
                assert parse_tree[0].type == 'term'
                return self.compile_expression(parse_tree[0])
            elif len(parse_tree.value) == 3:
                return (
                    self.compile_expression(parse_tree[0]) +
                    self.compile_expression(parse_tree[2]) +
                    self.compile_op(parse_tree[1])
                )
            else:
                raise ValueError('{} is not a valid expression'.format(parse_tree)) 

    def compile_unary_op(self, op_symbol):
        assert op_symbol.type == 'symbol'
        symbol_ops = {
            '~': 'not\n',
            '-': 'neg\n',
        }
        return symbol_ops[op_symbol.value]

    def compile_op(self, op_symbol):
        assert op_symbol.type == 'symbol'
        symbol_ops = {
            '+': 'add\n',
            '-': 'sub\n',
            '*': 'call Math.multiply\n',
            '/': 'call Math.divide\n',
            '&': 'and\n',
            '|': 'or\n',
            '>': 'gt\n',
            '<': 'lt\n',
            '=': 'eq\n',
        }
        return symbol_ops[op_symbol.value]

    def compile_subroutine_call(self, parse_list):
        assert parse_list[0].type == 'identifier'
        # Call on variable or class
        if parse_list[1].value == '.':
            # ( className | varName) '.' subroutineName '('expressionList ')'
            assert parse_list[3].value == '(' and parse_list[5].value == ')'
            try:
                # Object method
                obj = self._get_variable(parse_list[0].value)
                class_name = obj['type']
                push_pointer = 'push {kind} {id}\n'.format(**obj)
                pointer_arg_count = 1
            except GetVariableError:
                # Function or constructor
                class_name = parse_list[0].value
                push_pointer = ''
                pointer_arg_count = 0
            subroutine_name = parse_list[2].value
            expression_list = parse_list[4]
            nargs = len(self.get_expression_list_terms(parse_list[4])) + pointer_arg_count
            subroutine_call = 'call {}.{} {}\n'.format(class_name, subroutine_name, nargs)
            return (
                push_pointer + 
                self.compile_expression_list(parse_list[4]) +
                subroutine_call
            )
        # Call on private subroutine
        else:
            # subroutineName '(' expressionList ')'
            assert parse_list[1].value == '(' and parse_list[3].value == ')'
            this = self._get_variable('this')
            subroutine_name = parse_list[0].value
            nargs = len(self.get_expression_list_terms(parse_list[2])) + 1  # +1 for 'this'

            push_pointer = 'push {kind} {id}\n'.format(**this)
            subroutine_call = 'call {}.{} {}\n'.format(this['type'], subroutine_name, nargs) 
            return (
                push_pointer +
                self.compile_expression_list(parse_list[2]) +
                subroutine_call
            )

    def get_expression_list_terms(self, parse_tree):
        assert parse_tree.type == 'expressionList'
        return [t for t in parse_tree if t.type in ('expression', 'term')]

    def compile_expression_list(self, parse_tree):
        return ''.join([
            self.compile_expression(t) 
            for t in self.get_expression_list_terms(parse_tree) 
        ])

    def _get_variable(self, name):
        try:
            var = self.subroutine_symbols[name]
        except KeyError:
            try:
                var = self.class_symbols[name]
            except KeyError:
                raise GetVariableError
        return var

    def _get_label(self):
        label = 'L{}'.format(self.label_count)
        self.label_count += 1
        return label


class GetVariableError(KeyError):
    pass
