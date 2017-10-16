"""
Compiles a parse tree into Jack VM instructions
"""

class CodeGenerator(object):
    def __init__(self):
        self.class_symbols = {}
        self.subroutine_symbols = {}
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
                    'kind': 'var',
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
        pass

    def compile_let(self):
        pass

    def compile_do(self):
        # just do subroutine_call then pop the value off
        pass

    def compile_if(self):
        pass

    def compile_while(self):
        pass

    def compile_return(self):
        pass

    def compile_expression(self, parse_tree):
        # TODO: Start testing
        assert parse_tree.type in ('expression', 'term')

        if parse_tree.type == 'term':
            assert len(parse_tree.value) == 1
            term = parse_tree.value[0]
            if term.type == 'integerConstant':
                # Numbers
                return 'push constant {}\n'.format(term.value)
            elif term.type == 'stringConstant':
                # Strings
                string = term.value
                # String constants are handled using the OS constructor String.new(length) 
                # and the OS method String.appendChar(nextChar).
                # push constant LEN
                # call String.new 1
                # Then a bunch of subroutine calls for the obj
            elif term.type == 'identifier':
                # Variables
                variable = self._get_variable(term.value)
                return 'push {kind} {id}\n'.format(**variable)
            elif term.type == 'keyword':
                # Keyword constants 'true' | 'false' | 'null' | 'this' 
                if term.value == 'this':
                    variable = self._get_variable(term.value)
                    return 'push {kind} {id}\n'.format(**variable)
                elif term.value in ('null', 'false'):
                    return 'push constant 0\n'
                elif term.value == 'true':
                    return 'push constant 1\nneg\n'
                else:
                    raise ValueError('{} is not a valid keyword'.format(term))
            elif False:
                pass # Array access varName [ ex ]
            elif False:
                pass # subroutine call
            elif term.has_children and term.type == 'symbol' :
                # Unary operations
                assert len(term.value) == 2
                return self.compile_expression(term[1]) + self.compile_unary_op(term[0])
            elif term.has_children and term[0].value == '(' and term[-1].value == ')':
                # ( expression )
                assert len(term.value) == 3
                return self.compile_expression(term[1])
            else:
                raise ValueError('{} is not a valid term'.format(term))
        elif parse_tree.type == 'expression':
            if len(parse_tree.value) == 1:
                assert parse_tree.value.type == 'term'
                return self.compile_expression(parse_tree[0])
            elif len(parse_tree.value) == 3:
                return (
                    self.compile_expression(parse_tree[0]) +
                    self.compile_op(parse_tree[1]) +
                    self.compile_expression(parse_tree[2])
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

    def compile_subroutine_call(self):
        # leave return value on the stack
        pass

    def compile_expression_list(self):
        pass

    def _get_variable(self, name):
        try:
            var = self.subroutine_symbols[name]
        except KeyError:
            var = self.class_symbols[name]
        return var