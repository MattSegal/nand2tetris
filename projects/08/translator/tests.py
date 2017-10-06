from unittest import TestCase

import VMTranslator as trans


class TestParsePush(TestCase):
    def test_push_constant(self):
        args = ['Filename', 'constant', '7']
        expected = (
            '// push constant 7\n'
            '@7\n'
            'D=A\n'
            '@SP\n'
            'A=M\n'
            'M=D\n'
            '@SP\n'
            'M=M+1\n'
        )
        actual = trans.parse_push(*args)
        self.assertEqual(expected, actual)

    def test_push_static(self):
        args = ['Filename', 'static', '7']
        expected = (
            '// push static 7\n'
            '@Filename.7\n'
            'D=M\n'
            '@SP\n'
            'A=M\n'
            'M=D\n'
            '@SP\n'
            'M=M+1\n'
        )
        actual = trans.parse_push(*args)
        self.assertEqual(expected, actual)

    def test_push_local(self):
        args = ['Filename', 'local', '7']
        expected = (
            '// push local 7\n'
            '@7\n'
            'D=A\n'
            '@LCL\n'
            'A=D+M\n'
            'D=M\n'
            '@SP\n'
            'A=M\n'
            'M=D\n'
            '@SP\n'
            'M=M+1\n'
        )
        actual = trans.parse_push(*args)
        self.assertEqual(expected, actual)
    
    def test_push_argument(self):
        args = ['Filename', 'argument', '7']
        expected = (
            '// push argument 7\n'
            '@7\n'
            'D=A\n'
            '@ARG\n'
            'A=D+M\n'
            'D=M\n'
            '@SP\n'
            'A=M\n'
            'M=D\n'
            '@SP\n'
            'M=M+1\n'
        )
        actual = trans.parse_push(*args)
        self.assertEqual(expected, actual)

    def test_push_this(self):
        args = ['Filename', 'this', '7']
        expected = (
            '// push this 7\n'
            '@7\n'
            'D=A\n'
            '@THIS\n'
            'A=D+M\n'
            'D=M\n'
            '@SP\n'
            'A=M\n'
            'M=D\n'
            '@SP\n'
            'M=M+1\n'
        )
        actual = trans.parse_push(*args)
        self.assertEqual(expected, actual)

    def test_push_that(self):
        args = ['Filename', 'that', '7']
        expected = (
            '// push that 7\n'
            '@7\n'
            'D=A\n'
            '@THAT\n'
            'A=D+M\n'
            'D=M\n'
            '@SP\n'
            'A=M\n'
            'M=D\n'
            '@SP\n'
            'M=M+1\n'
        )
        actual = trans.parse_push(*args)
        self.assertEqual(expected, actual)

    def test_push_temp(self):
        args = ['Filename', 'temp', '3']
        expected = (
            '// push temp 3\n'
            '@3\n'
            'D=A\n'
            '@5\n'
            'A=D+A\n'
            'D=M\n'
            '@SP\n'
            'A=M\n'
            'M=D\n'
            '@SP\n'
            'M=M+1\n'
        )
        actual = trans.parse_push(*args)
        self.assertEqual(expected, actual)

    def test_push_pointer_0(self):
        args = ['Filename', 'pointer', '0']
        expected = (
            '// push pointer 0\n'
            '@THIS\n'
            'D=M\n'
            '@SP\n'
            'A=M\n'
            'M=D\n'
            '@SP\n'
            'M=M+1\n'
        )
        actual = trans.parse_push(*args)
        self.assertEqual(expected, actual)

    def test_push_pointer_1(self):
        args = ['Filename', 'pointer', '1']
        expected = (
            '// push pointer 1\n'
            '@THAT\n'
            'D=M\n'
            '@SP\n'
            'A=M\n'
            'M=D\n'
            '@SP\n'
            'M=M+1\n'
        )
        actual = trans.parse_push(*args)
        self.assertEqual(expected, actual)


class TestParsePop(TestCase):
    # Decrement stack pointer
    # Set D to current stack value
    DECREMENT_SP_AND_LOAD_STACK ='@SP\nM=M-1\nA=M\nD=M\n'
    
    def test_pop_static(self):
        args = ['Filename', 'static', '7']
        expected = (
            '// pop static 7\n' 
            + self.DECREMENT_SP_AND_LOAD_STACK +
            '@Filename.7\n'
            'M=D\n'
        )
        actual = trans.parse_pop(*args)
        self.assertEqual(expected, actual)

    def test_pop_local(self):
        args = ['Filename', 'local', '7']
        expected = (
            '// pop local 7\n'
            '@7\n'
            'D=A\n'
            '@LCL\n'
            'D=D+M\n'
            '@R13\n'
            'M=D\n' 
            + self.DECREMENT_SP_AND_LOAD_STACK +
            '@R13\n'
            'A=M\n'
            'M=D\n'
        )
        actual = trans.parse_pop(*args)
        self.assertEqual(expected, actual)
    
    def test_pop_argument(self):
        args = ['Filename', 'argument', '7']
        expected = (
            '// pop argument 7\n'
            '@7\n'
            'D=A\n'
            '@ARG\n'
            'D=D+M\n'
            '@R13\n'
            'M=D\n' 
            + self.DECREMENT_SP_AND_LOAD_STACK +
            '@R13\n'
            'A=M\n'
            'M=D\n'
        )
        actual = trans.parse_pop(*args)
        self.assertEqual(expected, actual)

    def test_pop_this(self):
        args = ['Filename', 'this', '7']
        expected = (
            '// pop this 7\n'
            '@7\n'
            'D=A\n'
            '@THIS\n'
            'D=D+M\n'
            '@R13\n'
            'M=D\n' 
            + self.DECREMENT_SP_AND_LOAD_STACK +
            '@R13\n'
            'A=M\n'
            'M=D\n'
        )
        actual = trans.parse_pop(*args)
        self.assertEqual(expected, actual)

    def test_pop_that(self):
        args = ['Filename', 'that', '7']
        expected = (
            '// pop that 7\n'
            '@7\n'
            'D=A\n'
            '@THAT\n'
            'D=D+M\n'
            '@R13\n'
            'M=D\n' 
            + self.DECREMENT_SP_AND_LOAD_STACK +
            '@R13\n'
            'A=M\n'
            'M=D\n'
        )
        actual = trans.parse_pop(*args)
        self.assertEqual(expected, actual)

    def test_pop_temp(self):
        args = ['Filename', 'temp', '7']
        expected = (
            '// pop temp 7\n'
            '@7\n'
            'D=A\n'
            '@5\n'
            'D=D+A\n'
            '@R13\n'
            'M=D\n' 
            + self.DECREMENT_SP_AND_LOAD_STACK +
            '@R13\n'
            'A=M\n'
            'M=D\n'
        )
        actual = trans.parse_pop(*args)
        self.assertEqual(expected, actual)

    def test_pop_pointer_0(self):
        args = ['Filename', 'pointer', '0']
        expected = (
            '// pop pointer 0\n' 
            + self.DECREMENT_SP_AND_LOAD_STACK +
            '@THIS\n'
            'M=D\n'
        )
        actual = trans.parse_pop(*args)
        self.assertEqual(expected, actual)

    def test_pop_pointer_1(self):
        args = ['Filename', 'pointer', '1']
        expected = (
            '// pop pointer 1\n' 
            + self.DECREMENT_SP_AND_LOAD_STACK +
            '@THAT\n'
            'M=D\n'
        )
        actual = trans.parse_pop(*args)
        self.assertEqual(expected, actual)


class TestCleaning(TestCase):
    def test_clean_text(self):
        vm_text = (
            '// by Nisan and Schocken, MIT Press.\n'
            '// File name: projects/06/add/Add.asm\n'
            '// Computes R0 = 2 + 3  (R0 refers to RAM[0])\n'
            ' // Woah! \n'
            'push constant 8\n'
            'add\n'
            '\tsub \n'
            ' pop this // No Good!\n'
        )
        expected = [['push', 'constant', '8'], ['add'], ['sub'], ['pop', 'this']]
        actual = trans.clean_text(vm_text)
        self.assertEqual(expected, actual)

