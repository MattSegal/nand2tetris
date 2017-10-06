from unittest import TestCase

import assembler


class TestParseASM(TestCase):
    def test_parse_multiplication(self):
        asm_text = """
        // Multiplies R0 and R1 and stores the result in R2.
        // (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

        // Initialise R2 to 0
        @R2
        M=0

        // Write value from R1 into counter, so that we don't mutate R1
        @R1
        D=M
        @counter
        M=D

        (LOOP)
            // Exit loop if value in counter is 0
            @counter
            D=M
            @END
            D;JEQ

            // Increment R2 by R0
            @R0
            D=M
            @R2
            M=M+D

            // Decrement counter
            @counter
            M=M-1

            @LOOP
            0;JMP

        (END)
            @END
            0;JMP
        """ 
        expected = """
        0000000000000010
        1110101010001000
        0000000000000001
        1111110000010000
        0000000000010000
        1110001100001000
        0000000000010000
        1111110000010000
        0000000000010010
        1110001100000010
        0000000000000000
        1111110000010000
        0000000000000010
        1111000010001000
        0000000000010000
        1111110010001000
        0000000000000110
        1110101010000111
        0000000000010010
        1110101010000111
        """[1:].replace(' ', '')

        actual = assembler.parse_asm(asm_text)
        self.assertEqual(len(expected), len(actual))

        # ex_lines = expected.split('\n')
        # ac_lines = actual.split('\n')
        # print
        # for i in range(len(ex_lines)):
        #     print "{}\t{}\t{} {}".format(ex_lines[i], ac_lines[i], i, ex_lines[i] == ac_lines[i])


        # print actual
        self.assertEqual(expected,actual)


class TestParseSymbols(TestCase):
    def test_parse_variables(self):
        lines = [
            '@1',
            'A=D+A',
            '@FOO',
            '0;JMP',
            '@2',
            '@R3',
            '@BAR',
            '0;JMP',
            '@FOO',
            '0;JMP',
            '@FOO',
            '0;JMP',
        ]
        expected_symbols = {
            'FOO': 16,
            'BAR': 17,
        }
        expected_symbols.update(assembler.CONSTANT_VARIABLES)
        actual_symbols = assembler.parse_symbols(lines)
        self.assertEqual(expected_symbols, actual_symbols)

    def test_parse_labels(self):
        lines = [
            '@1',
            'A=D+A',
            '@FOO',
            '0;JMP',
            '@2',
            '@BAR',
            '0;JMP',
            '@R3',
            '(FOO)',
            '0;JMP',
            '(BAR)',
            '0;JMP',
        ]
        expected_symbols = {
            'FOO': 8,
            'BAR': 9,
        }
        expected_symbols.update(assembler.CONSTANT_VARIABLES)
        actual_symbols = assembler.parse_symbols(lines)
        self.assertEqual(expected_symbols, actual_symbols)

    def test_parse_variables_and_labels(self):
        lines = [
            '@1',
            'A=D+A',
            '@FOO',
            '0;JMP',
            '@BAZ',
            '0;JMP',
            '@BAR',
            '0;JMP',
            '@FOO',
            '0;JMP',
            'A=D+A',
            '@R3',
            '@FOO',
            '0;JMP',
            '@BAR',
            '(FOO)',
            '0;JMP',
            '(BAR)',
            '0;JMP',
            '@BAZ',
        ]
        expected_symbols = {
            'FOO': 15,
            'BAR': 16,
            'BAZ': 16,
        }
        expected_symbols.update(assembler.CONSTANT_VARIABLES)
        actual_symbols = assembler.parse_symbols(lines)
        self.assertEqual(expected_symbols, actual_symbols)


class TestParseCInstruction(TestCase):
    def test_op_code(self):
        line = 'AMD=0;JMP'
        instruction = assembler.parse_c_instruction(line)
        expected_op_code = '111'
        self.assertEqual(expected_op_code, instruction[:3])

    def test_a_flag_m(self):
        line = 'D=D+A'
        instruction = assembler.parse_c_instruction(line)
        expected_a_flag = '0'
        self.assertEqual(expected_a_flag, instruction[3])

    def test_a_flag_a(self):
        line = 'D=D+M'
        instruction = assembler.parse_c_instruction(line)
        expected_a_flag = '1'
        self.assertEqual(expected_a_flag, instruction[3])

    def test_a_flag_default(self):
        line = 'D=1'
        instruction = assembler.parse_c_instruction(line)
        expected_a_flag = '0'
        self.assertEqual(expected_a_flag, instruction[3])

    def test_d_and_a(self):
        line = 'M=D&A;JLE'
        instruction = assembler.parse_c_instruction(line)
        expected_comp_code = '000000'
        self.assertEqual(expected_comp_code, instruction[4:10])

    def test_a_and_d(self):
        line = 'M=A&D;JLE'
        instruction = assembler.parse_c_instruction(line)
        expected_comp_code = '000000'
        self.assertEqual(expected_comp_code, instruction[4:10])

    def test_m_minus_d(self):
        line = 'D=A-D;JNE'
        instruction = assembler.parse_c_instruction(line)
        expected_comp_code = '000111'
        self.assertEqual(expected_comp_code, instruction[4:10])

    def test_store_amd(self):
        line = 'AMD=0;JMP'
        instruction = assembler.parse_c_instruction(line)
        expected_dest_code = '111'
        self.assertEqual(expected_dest_code, instruction[10:13])

    def test_store_md(self):
        line = 'MD=0;JMP'
        instruction = assembler.parse_c_instruction(line)
        expected_dest_code = '011'
        self.assertEqual(expected_dest_code, instruction[10:13])

    def test_store_m(self):
        line = 'M=0;JMP'
        instruction = assembler.parse_c_instruction(line)
        expected_dest_code = '001'
        self.assertEqual(expected_dest_code, instruction[10:13])

    def test_store_nowhere(self):
        line = '0;JMP'
        instruction = assembler.parse_c_instruction(line)
        expected_dest_code = '000'
        self.assertEqual(expected_dest_code, instruction[10:13])

    def test_no_jump(self):
        line = 'D=A'
        instruction = assembler.parse_c_instruction(line)
        expected_jump_code = '000'
        self.assertEqual(expected_jump_code, instruction[13:])

    def test_unconditional_jump(self):
        line = 'D=A;JMP'
        instruction = assembler.parse_c_instruction(line)
        expected_jump_code = '111'
        self.assertEqual(expected_jump_code, instruction[13:])

    def test_jump_gt_zero(self):
        line = 'D=A;JGT'
        instruction = assembler.parse_c_instruction(line)
        expected_jump_code = '001'
        self.assertEqual(expected_jump_code, instruction[13:])

    def test_jump_eq_zero(self):
        line = 'D=A;JEQ'
        instruction = assembler.parse_c_instruction(line)
        expected_jump_code = '010'
        self.assertEqual(expected_jump_code, instruction[13:])

    def test_jump_lt_zero(self):
        line = 'D=A;JLT'
        instruction = assembler.parse_c_instruction(line)
        expected_jump_code = '100'
        self.assertEqual(expected_jump_code, instruction[13:])


class TestParseAInstruction(TestCase):
    def test_zero(self):
        address = 0
        expected = '0000000000000000'
        actual = assembler.parse_a_instruction(address)
        self.assertEqual(expected, actual)

    def test_one(self):
        address = 1
        expected = '0000000000000001'
        actual = assembler.parse_a_instruction(address)
        self.assertEqual(expected, actual)

    def test_two(self):
        address = 2
        expected = '0000000000000010'
        actual = assembler.parse_a_instruction(address)
        self.assertEqual(expected, actual)


class TestCleaning(TestCase):
    def test_clean_text(self):
        asm_text = (
            '// by Nisan and Schocken, MIT Press.\n'
            '// File name: projects/06/add/Add.asm\n'
            '// Computes R0 = 2 + 3  (R0 refers to RAM[0])\n'
            ' // Woah! \n'
            '\t@2 \n'
            ' D=A // No Good!\n'
        )
        expected = ['@2', 'D=A']
        actual = assembler.clean_text(asm_text)
        self.assertEqual(expected, actual)

    def test_strip_spaces(self):
        asm_text = (
            '\t@ 2 \n '
            '  D = A \n'
        )
        expected = ['@2', 'D=A']
        actual = assembler.clean_text(asm_text)
        self.assertEqual(expected, actual)

    def test_strip_comments(self):
        asm_text = (
            '// by Nisan and Schocken, MIT Press.\n'
            '// File name: projects/06/add/Add.asm\n'
            '// Computes R0 = 2 + 3  (R0 refers to RAM[0])\n'
            '@2 // This was a good one! // Too many comments!\n'
            'D=A\n'
        )
        expected = ['@2', 'D=A']
        actual = assembler.clean_text(asm_text)
        self.assertEqual(expected, actual)

    def test_strip_newlines(self):
        asm_text = (
            '\n'
            '@2\n'
            '\n'
            'D=A\n'
            '\n'
        )
        expected = ['@2', 'D=A']
        actual = assembler.clean_text(asm_text)
        self.assertEqual(expected, actual)


class TestDecimalToBinary(TestCase):
    def test_zero(self):
        integer = 0
        expected = '000000000000000'
        actual = assembler.decimal_to_binary(integer)
        self.assertEqual(expected, actual)

    def test_one(self):
        integer = 1
        expected = '000000000000001'
        actual = assembler.decimal_to_binary(integer)
        self.assertEqual(expected, actual)

    def test_two(self):
        integer = 2
        expected = '000000000000010'
        actual = assembler.decimal_to_binary(integer)
        self.assertEqual(expected, actual)

    def test_five(self):
        integer = 5
        expected = '000000000000101'
        actual = assembler.decimal_to_binary(integer)
        self.assertEqual(expected, actual)

    def test_twenty_one(self):
        integer = 21
        expected = '000000000010101'
        actual = assembler.decimal_to_binary(integer)
        self.assertEqual(expected, actual)

    def test_max_val(self):
        integer = 2**15 - 1
        expected = '111111111111111'
        actual = assembler.decimal_to_binary(integer)
        self.assertEqual(expected, actual)
