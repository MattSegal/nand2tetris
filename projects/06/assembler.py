"""
Assembles Hack ASM files into the Hack machine code
"""

CONSTANT_VARIABLES = {
    'R0': 0,   'R1': 1,   'R2': 2,   'R3': 3,
    'R4': 4,   'R5': 5,   'R6': 6,   'R7': 7,
    'R8': 8,   'R9': 9,   'R10': 10, 'R11': 11,
    'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
    'SCREEN': 16384, 'KBD': 24576,
    'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4
}

JUMP_CODE_MAP = {
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}

DEST_CODE_MAP = {
    'M': '001',
    'D': '010',
    'MD': '011',
    'A': '100',
    'AM': '101',
    'AD': '110',
    'AMD': '111'
}

COMP_CODE_MAP = {
    '0':    '101010',
    '1':    '111111',
    '-1':   '111010',
    'D':    '001100',
    'A':    '110000',
    '!D':   '001101',
    '!A':   '110001',
    '-D':   '001111',
    '-A':   '110011',
    'D+1':  '011111',
    'A+1':  '110111',
    'D-1':  '001110',
    'A-1':  '110010',
    'D+A':  '000010',
    'D-A':  '010011',
    'A-D':  '000111',
    'D&A':  '000000',
    'D|A':  '010101'
}


def main(filename):
    import os

    with open(filename, 'r') as f:
        asm_text = f.read()

    output_text = parse_asm(asm_text)
    
    output_filename = os.path.join(
        'submission',
        os.path.split(filename)[-1].replace('.asm', '.hack')
    )
    with open(output_filename, 'w') as f:
        asm_text = f.write(output_text)


def parse_asm(asm_text):
    """
    IAMA Docstring
    """
    parsed_text = ''
    lines = clean_text(asm_text)
    symbols = parse_symbols(lines)

    for line in lines:
        if line[0] == '(':
            # Ignore code block symbols
            continue

        if line[0] == '@':
            address = line[1:]
            address = symbols[address] if address in symbols else address
            instruction = parse_a_instruction(address)

        else:
            instruction = parse_c_instruction(line)

        parsed_text += instruction + '\n'

    return parsed_text


def parse_symbols(lines):
    """
    Parse labels and variables from 
    """
    symbols = {}
    symbols.update(CONSTANT_VARIABLES)

    # Parse labels first
    line_count = 0  # TODO: Do we start at 0 or 1?
    for line in lines:
        if line[0] == '(':
            label = line[1:-1]
            symbols[label] = line_count
        else:
            line_count += 1

    # Parse variables
    available_register = 16
    for line in lines:
        if line[0] == '@' and not str.isdigit(line[1:]):
            variable = line[1:]
            if variable not in symbols:
                symbols[variable] = available_register
                available_register += 1

    return symbols


def parse_c_instruction(line):
    """
    Parses a C instruction into machine code    
    """
    jump_split = line.split(';')
    dest_comp_split = jump_split[0].split('=')

    jump_instruction = jump_split[1] if len(jump_split) > 1 else None
    dest_instruction = dest_comp_split[0] if len(dest_comp_split) > 1 else None
    comp_instruction = dest_comp_split[1] if dest_instruction else dest_comp_split[0]

    # Start with OP code
    machine_code = '111'

    # Set 'a' flag
    if 'M' in comp_instruction:
        machine_code += '1'
        comp_instruction = comp_instruction.replace('M', 'A')
    else:
        machine_code += '0'

    # Parse computation instruction
    if len(comp_instruction) == 3:
        alternate_comp = comp_instruction[2] + comp_instruction[1] + comp_instruction[0]
    else:
        alternate_comp = None

    comp_code = COMP_CODE_MAP.get(comp_instruction)
    alt_compt_code = COMP_CODE_MAP.get(alternate_comp)
    if not comp_code and not alt_compt_code:
        raise ValueError('Invalid computation instruction %s' % comp_instruction)

    machine_code += comp_code if comp_code else alt_compt_code

    # Parse destination instruction
    if dest_instruction:
        try:
            machine_code += DEST_CODE_MAP[dest_instruction]
        except KeyError:
            raise ValueError('Invalid destination instruction %s' % dest_instruction)
    else:
        machine_code += '000'

    # Parse jump instruction
    if jump_instruction:
        try:
            machine_code += JUMP_CODE_MAP[jump_instruction]
        except KeyError:
            raise ValueError('Invalid jump instruction %s' % jump_instruction)
    else:
        machine_code += '000'

    return machine_code


def parse_a_instruction(address):
    """
    Parse an address integer into an A instruction
    returns: machine code
    """
    decimal = int(address)
    return '0' + decimal_to_binary(decimal)


def clean_text(asm_text):
    """
    Strip all comments, empty lines and whitespace from the text
    """
    parse_line = lambda l : line.split('//')[0].replace(' ','').replace('\t', '')
    return [
        parse_line(line) for line in asm_text.split('\n')
        if parse_line(line)
    ]


def decimal_to_binary(integer):
    """
    Converts an integer into a 15 bit binary string
    """
    binary_string = ''
    for i in range(15):
        binary_string = str(integer % 2) + binary_string
        integer = integer / 2

    return binary_string


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
