"""
Assembles Hack ASM files into the Hack machine code
"""
import os.path

def main(filename):
    with open(filename, 'r') as f:
        vm_text = f.read()

    file_base_name = os.path.basename(filename).split('.')[0]  # For static variable symbol
    output_text = parse_vm_to_asm(vm_text, file_base_name)
    
    output_filename = filename.replace('.vm', '.asm')
    with open(output_filename, 'w') as f:
        f.write(output_text)


def parse_vm_to_asm(vm_text, file_base_name):
    """
    Parses a string on vm commands to a string of asm commands
    for the Hack computer
    """
    lines = clean_text(vm_text)
    parsed_lines = [
        COMMAND_MAP[line[0]](file_base_name, *line[1:]) 
        for line in lines
    ]
    return '\n'.join(parsed_lines)


COMMAND_MAP = {
    'push': lambda *args: parse_push(*args),
    'pop':  lambda *args: parse_pop(*args),
    'add':  lambda *args: parse_add(*args),
    'sub':  lambda *args: parse_sub(*args),
    'neg':  lambda *args: parse_neg(*args),
    'eq':   lambda *args: parse_eq(*args),
    'gt':   lambda *args: parse_gt(*args),
    'lt':   lambda *args: parse_lt(*args),
    'and':  lambda *args: parse_and(*args),
    'or':   lambda *args: parse_or(*args),
    'not':  lambda *args: parse_not(*args)
}


def parse_push(file_name, *args):
    """
    A push command copies the specified register
    onto the top of the stack and increments the stack pointer
    """
    v_section = args[0]
    v_addr = args[1]

    # Each different virtual operation requires a different
    # value to be pushed into the D register
    if v_section == 'constant':
        # Store constant value in D
        load_val = '@{a}\nD=A\n'.format(a=v_addr)
    elif v_section == 'static':
        # Store static symbol value in D
        load_val = '@{f}.{a}\nD=M\n'.format(f=file_name, a=v_addr)
    elif v_section == 'pointer':
        # Store pointer reference in D
        symbol = 'THAT' if int(v_addr) else 'THIS'
        load_val = '@{s}\nD=M\n'.format(s=symbol)
    else:
        symbol_map = {
            # symbol, memory location
            'local':    ('LCL', 'M'),
            'argument': ('ARG', 'M'),
            'this':     ('THIS', 'M'),
            'that':     ('THAT', 'M'),
            'temp':     ('5', 'A'),
        }
        symbol, loc = symbol_map[v_section]
        load_val = (
            '@{a}\n'    # Load relative memory ref into D
            'D=A\n'     # -
            '@{s}\n'    # Select absolute memory location
            'A=D+{l}\n' # -
            'D=M\n'     # Load selected memory into D
        ).format(a=v_addr, s=symbol, l=loc)

    return (
        '// push {v_section} {v_addr}\n'
        # Store pushed value in the D register
        '{load_val}'
        # Push D onto the stack
        '@SP\nA=M\nM=D\n'
        # Increment stack pointer
        '@SP\nM=M+1\n'
    ).format(
        v_section=v_section,
        v_addr=v_addr,
        load_val=load_val
    )


def parse_pop(file_name, *args):
    """
    A pop command copies the top of the stack into
    the specified register and decrements the stack pointer
    """
    v_section = args[0]
    v_addr = args[1]

    # Each different virtual operation requires the
    # D register to be pushed to a different place

    if v_section == 'static':
        # Write value to static symbol
        write_val = '@{f}.{a}\nM=D\n'.format(f=file_name, a=v_addr)
        stash_addr = ''  # No need
    elif v_section == 'pointer':
        # Write value to pointer address
        symbol = 'THAT' if int(v_addr) else 'THIS'
        write_val = '@{s}\nM=D\n'.format(s=symbol)
        stash_addr = ''  # No need
    else:
        symbol_map = {
            # symbol, memory location
            'local':    ('LCL', 'M'),
            'argument': ('ARG', 'M'),
            'this':     ('THIS', 'M'),
            'that':     ('THAT', 'M'),
            'temp':     ('5', 'A'),
        }
        symbol, loc = symbol_map[v_section]
        stash_addr = (
            '@{a}\n'    # Load relative memory ref into D
            'D=A\n'     # -
            '@{s}\n'    # Load relative + absolute memory refs into D
            'D=D+{l}\n' # -
            '@R13\n'    # Stash address in R13
            'M=D\n'     # - 
        ).format(a=v_addr, s=symbol, l=loc)
        write_val = (
            '@R13\n'    # Select stashed address from R13 
            'A=M\n'     # -
            'M=D\n'     # Write D to that address           
        ).format(v_addr, symbol)

    return (
        '// pop {v_section} {v_addr}\n'
        '{stash_addr}'  # Stash target address
        '@SP\n'         # Decrement stack pointer
        'M=M-1\n'       # -   
        'A=M\n'         # Select the top of the stack
        'D=M\n'         # Store the top of the stack in D
        '{write_val}'   # Write D into the target register
    ).format(
        v_section=v_section,
        v_addr=v_addr,
        stash_addr=stash_addr,
        write_val=write_val
    )


# SP-1 is selected as M
UNARY_SETUP = (
    '// {name}\n'
    '@SP\n'
    'A=M-1\n'   # Select SP-1
)


def parse_neg(*args):
    # SP-1 is M
    return UNARY_SETUP.format(name='neg') + 'M=-M\n'


def parse_not(*args):
    # SP-1 is M
    return UNARY_SETUP.format(name='not') + 'M=!M\n'


# SP-1 is stored in into D
# SP-2 is selected as M
# SP has been decremented
ARITHMETIC_SETUP = (
    '// {name}\n'
    '@SP\n'
    'M=M-1\n'   # Decrement SP
    'D=M\n'     # Store SP-1 in D
    '@R13\n'    # Store SP-2 in R13
    'M=D-1\n'   # -
    'A=D\n'     # Select SP-1, store value in D
    'D=M\n'     # -
    '@R13\n'    # Select SP-2
    'A=M\n'     # -
)


def parse_add(*args):
    # SP-2 is M, SP-1 is D    
    return ARITHMETIC_SETUP.format(name='add') + 'M=D+M\n'

def parse_sub(*args):
    # SP-2 is M, SP-1 is D    
    return ARITHMETIC_SETUP.format(name='sub') + 'M=M-D\n'

def parse_and(*args):
    # SP-2 is M, SP-1 is D    
    return ARITHMETIC_SETUP.format(name='and') + 'M=M&D\n'

def parse_or(*args):
    # SP-2 is M, SP-1 is D    
    return ARITHMETIC_SETUP.format(name='or') + 'M=M|D\n'


COMPARISON_SETUP = (
    '// {name}\n'
    # Decrement SP
    # Store SP-2 - SP-1 in D
    '@SP\n'
    'M=M-1\n'   # Decrement SP
    'D=M\n'     # Store SP-1 in D
    '@R13\n'    # Store SP-2 in R13
    'M=D-1\n'   # -
    'A=D\n'     # Select SP-1, store value in D
    'D=M\n'     # -
    '@R13\n'    # Select SP-2
    'A=M\n'     # -
    'D=M-D\n'   # Store SP-2 - SP-1 in D

    # Conditional jump
    '{select_t}'# Jump to TRUE if D satisfies comp
    'D;{comp}\n'# -

    # False section
    '@0\n'      # Store 0 in D for 'false'
    'D=A\n'     # -
    '{select_f}'# Jump to FALSE to skip true section
    '0;JMP\n'   # -

    # True section
    '{t_label}' # True section
    '@1\n'      # Store -1 in D for 'true'
    'D=-A\n'    # -

    # Write result
    '{f_label}'
    '@SP\n'     # Select SP-2 (SP already decremented by 1)
    'A=M-1\n'   # -
    'M=D\n'     # Write result in SP-2
)

if_counter = 0

def get_if_labels():
    global if_counter
    labels = (
        '@TRUE_{}\n'.format(if_counter),
        '(TRUE_{})\n'.format(if_counter),
        '@FALSE_{}\n'.format(if_counter),
        '(FALSE_{})\n'.format(if_counter)
    )
    if_counter += 1
    return labels


def parse_eq(*args):
    select_t, t_label, select_f, f_label = get_if_labels()
    return COMPARISON_SETUP.format(
        name='eq',
        comp='JEQ',
        select_t=select_t,
        select_f=select_f,
        t_label=t_label,
        f_label=f_label,
    )


def parse_gt(*args):
    select_t, t_label, select_f, f_label = get_if_labels()
    return COMPARISON_SETUP.format(
        name='gt',
        comp='JGT',
        select_t=select_t,
        select_f=select_f,
        t_label=t_label,
        f_label=f_label,
    )


def parse_lt(*args):
    select_t, t_label, select_f, f_label = get_if_labels()
    return COMPARISON_SETUP.format(
        name='lt',
        comp='JLT',
        select_t=select_t,
        select_f=select_f,
        t_label=t_label,
        f_label=f_label,
    )


def clean_text(vm_text):
    """
    Transforms program text into a list of lists
        'push constant 8\n'
        [['push', 'constant', '8']]
    Clean unwanted features from the text:
        - comments
        - empty lines
        - leading/trailing whitespace
    """
    parse_line = lambda l : (l
        .split('//')[0]
        .strip()
        .split(' ')
    )
    parsed_lines = (parse_line(line) for line in vm_text.split('\n'))
    return [
        line for line in parsed_lines if line[0]
    ]


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
