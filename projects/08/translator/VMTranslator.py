"""
Assembles Hack ASM files into the Hack machine code
"""
import os
import os.path as path

def main(input_node):
    """
    input   a directory or filename (foo.vm)
    output  directory_name.asm or filename.asm
    """
    if path.isdir(input_node):
        dir_path = path.dirname(input_node)
        dir_name = path.split(path.normpath(input_node))[-1]
        input_files = [
            path.join(input_node, f) for f in os.listdir(input_node) 
            if f.endswith('.vm')
        ]
        output_filename = '{}.asm'.format(path.join(input_node, dir_name))
    elif path.isfile(input_node) and input_node.endswith('.vm'):
        input_files = [input_node]
        output_filename = input_node.replace('.vm', '.asm')
    else:
        raise ValueError('{} is not a file or directory'.format(input_node))

    # Start with boostrap code
    call_sys = any(f_name.endswith('Sys.vm') for f_name in input_files)
    output_text = init_vm() if call_sys else ''

    # Parse each file
    for filename in input_files:
        with open(filename, 'r') as f:
            vm_text = f.read()

        # Get file name for scoping static variables, functions, etc
        file_base_name = path.basename(filename).split('.')[0]
        output_text += parse_vm_to_asm(vm_text, file_base_name)
    
    with open(output_filename, 'w') as f:
        f.write(output_text)


def init_vm():
    """Initialises the Hack VM"""
    return (
        '// Boostrap the Hack Virtual Machine\n'
        '@256\nD=A\n@SP\nM=D\n'  # Set stack pointer address
        #'@Sys.init\n0;JMP\n'  # Call Sys.init
    ) + parse_call('Sys.init', '0')


def parse_vm_to_asm(vm_text, file_base_name):
    """
    Parses a string on virtual machine commands
    to a string of asm commands for the Hack computer
    """
    # Remove comments and standardise formatting
    lines = clean_text(vm_text)

    # Add function and file based scoping
    add_scoping(lines, file_base_name)

    # Parse each line into ASM
    parsed_lines = [
        COMMAND_MAP[line[0]](*line[1:]) 
        for line in lines
    ]
    return '\n'.join(parsed_lines)


def add_scoping(lines, file_base_name):
    """
    Adds file scoping to static variables
    and function scoping to VM code labels
    """
    func_name = 'global'
    for line in lines:
        if line[0] == 'function':
            func_name = line[1]
        elif line[0] == 'return':
            func_name == 'global'
        elif len(line) > 1 and line[1] == 'static':
            line[1] = '{}.static'.format(file_base_name)
        elif line[0] in ('label', 'goto', 'if-goto'):
            line[1] = '{}.{}'.format(func_name, line[1])
        print line


COMMAND_MAP = {
    'push':     lambda *args: parse_push(*args),
    'pop':      lambda *args: parse_pop(*args),
    'add':      lambda *args: parse_add(*args),
    'sub':      lambda *args: parse_sub(*args),
    'neg':      lambda *args: parse_neg(*args),
    'eq':       lambda *args: parse_eq(*args),
    'gt':       lambda *args: parse_gt(*args),
    'lt':       lambda *args: parse_lt(*args),
    'and':      lambda *args: parse_and(*args),
    'or':       lambda *args: parse_or(*args),
    'not':      lambda *args: parse_not(*args),
    'label':    lambda *args: parse_label(*args),
    'goto':     lambda *args: parse_goto(*args),
    'if-goto':  lambda *args: parse_if_goto(*args),
    'function': lambda *args: parse_function(*args),
    'call':     lambda *args: parse_call(*args),
    'return':   lambda *args: parse_return(*args),
}


def parse_function(func_name, num_locals):
    """
    Declare the function entry point and 
    initialise the local variables on the stack

    Example (callee): 'function add 3'

    BEFORE              AFTER
    <blank>  <-SP, LCL  local 0 <- LCL
                        local 1
                        local 2
                        <blank> <- SP
    """
    function_definition = (
        '// function {f} {n}\n'
        '({f})\n'  #  function label
    ).format(f=func_name, n=num_locals) 
    # Push 0 onto the stack 'num_locals' times
    setup_local_memory = (
        '@0\nD=A\n'     # Push 0 into memory
        '@SP\nA=M\n'    # Go to SP - assume SP == LCL
    ) + int(num_locals) * (
        '@SP\nA=M\nM=D\n'    # Write 0 to top of stack
        '@SP\nM=M+1\n'       # Increment SP
    )
    return function_definition + setup_local_memory


def parse_call(func_name, num_args):
    """
    Calls the named function with the specified number of args
    Saves the context of the calling function to the stack
        - return address
        - locations of LCL, ARG, THIS, THAT
    Jumps to the called function
    
    Example (caller):  'call add 2'

    BEFORE          AFTER
    arg 0           arg 0        <- ARG 
    arg 1           arg 1
    <blank>  <-SP   return addr
                    saved LCL
                    saved ARG
                    saved THIS
                    saved THAT
                    <blank>      <- SP, LCL
    """
    return (
        '// call {f} {n}\n'
        # Save calling function context
        # push return address
        '@{ret}\nD=A\n'     # Store return address in the D register
        '@SP\nA=M\nM=D\n'   # Push D onto the stack
        '@SP\nM=M+1\n'      # Increment stack pointer        
        # push LCL
        '@LCL\nD=M\n'       
        '@SP\nA=M\nM=D\n'   
        '@SP\nM=M+1\n'      
        # push ARG
        '@ARG\nD=M\n'        
        '@SP\nA=M\nM=D\n'    
        '@SP\nM=M+1\n'      
        # push THIS
        '@THIS\nD=M\n'        
        '@SP\nA=M\nM=D\n'    
        '@SP\nM=M+1\n'  
        # push THAT
        '@THAT\nD=M\n'        
        '@SP\nA=M\nM=D\n'    
        '@SP\nM=M+1\n'  
        # reposition LCL for new function context
        '@SP\nD=M\n'
        '@LCL\nM=D\n'
        # reposition ARG to point to new arguments (ARG = SP - n - 5)
        '@SP\nD=M\n'
        '@{n}\nD=D-A\n'
        '@5\nD=D-A\n'
        '@ARG\nM=D\n'
        # jump to called function
        '@{f}\n0;JMP\n'
        # drop a label for the return
        '({ret})\n'  
    ).format(f=func_name, n=num_args, ret=get_return_label())  


return_counter = -1
def get_return_label():
    global return_counter
    return_counter += 1
    return 'RETURN_{}'.format(return_counter)


def parse_return():
    """
    Write the return value from the top of the stack to ARG
    Restore the state of the calling function
        - LCL, ARG, THIS, THAT
    Sets the stack pointer to ARG + 1
    Jump to return address

    Example (callee):  'return' after 'call add 2'

    BEFORE                  AFTER
    arg 0        <- ARG     34         
    arg 1                   <blank>  <- SP
    return addr
    saved LCL
    saved ARG
    saved THIS
    saved THAT
    12
    34
    <blank>      <- SP

    """
    return (
        '// return\n'
        # Store LCL in temp variable FRAME
        '@LCL\nD=M\n@FRAME\nM=D\n'
        # Store return address (FRAME-5) in temp variable
        '@FRAME\nD=M\n@5\nD=D-A\nA=D\nD=M\n'
        '@RET\nM=D\n'
        # Pop the top of the stack,
        # write it to ARG and reset the stack pointer
        '@SP\nA=M-1\nD=M\n'
        '@ARG\nA=M\nM=D\nD=A\n'
        '@SP\nM=D+1\n'

        # Restore THIS, THAT, ARG, LCL from saved context
        '@FRAME\nD=M\n@1\nD=D-A\nA=D\nD=M\n@THAT\nM=D\n'
        '@FRAME\nD=M\n@2\nD=D-A\nA=D\nD=M\n@THIS\nM=D\n'
        '@FRAME\nD=M\n@3\nD=D-A\nA=D\nD=M\n@ARG\nM=D\n'
        '@FRAME\nD=M\n@4\nD=D-A\nA=D\nD=M\n@LCL\nM=D\n'
        # Jump to the return address
        '@RET\nA=M\n0;JMP\n'
    )


def parse_label(label_name):
    """
    A label command marks a named waypoint for goto commands
    Labels are scoped by file and function
    """
    return (
        '// label {name}\n'
        '({name})\n'
    ).format(name=label_name)  


def parse_goto(label_name):
    """
    Unconditional goto a given label
    """
    return (
        '// goto {name}\n'
        '@{name}\n'
        '0;JMP\n'
    ).format(name=label_name)  


def parse_if_goto(label_name):
    """
    Jump based on the value of the topmost stack value (if !0)
    """
    return (
        '// if-goto {name}\n'
        '@SP\n'
        'M=M-1\n'   # Decrement SP
        'A=M\n'     # Select the top of the stack
        'D=M\n'     # Store the top of the stack in D
        '@{name}\n' # Select the target label
        'D;JNE\n'   # Jump if popped value > 0
    ).format(name=label_name)


def parse_push(v_section, v_addr):
    """
    A push command copies the specified register
    onto the top of the stack and increments the stack pointer
    """
    # Each different virtual operation requires a different
    # value to be pushed into the D register
    if v_section == 'constant':
        # Store constant value in D
        load_val = '@{a}\nD=A\n'.format(a=v_addr)
    elif v_section.endswith('static'):
        # Store static symbol value in D
        load_val = '@{static}.{a}\nD=M\n'.format(static=v_section, a=v_addr)
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


def parse_pop(v_section, v_addr):
    """
    A pop command copies the top of the stack into
    the specified register and decrements the stack pointer
    """
    # Each different virtual operation requires the
    # D register to be pushed to a different place
    if v_section.endswith('static'):
        # Write value to static symbol
        write_val = '@{static}.{a}\nM=D\n'.format(static=v_section, a=v_addr)
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


def parse_neg():
    # SP-1 is M
    return UNARY_SETUP.format(name='neg') + 'M=-M\n'


def parse_not():
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


def parse_add():
    # SP-2 is M, SP-1 is D    
    return ARITHMETIC_SETUP.format(name='add') + 'M=D+M\n'

def parse_sub():
    # SP-2 is M, SP-1 is D    
    return ARITHMETIC_SETUP.format(name='sub') + 'M=M-D\n'

def parse_and():
    # SP-2 is M, SP-1 is D    
    return ARITHMETIC_SETUP.format(name='and') + 'M=M&D\n'

def parse_or():
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


def parse_eq():
    select_t, t_label, select_f, f_label = get_if_labels()
    return COMPARISON_SETUP.format(
        name='eq',
        comp='JEQ',
        select_t=select_t,
        select_f=select_f,
        t_label=t_label,
        f_label=f_label,
    )


def parse_gt():
    select_t, t_label, select_f, f_label = get_if_labels()
    return COMPARISON_SETUP.format(
        name='gt',
        comp='JGT',
        select_t=select_t,
        select_f=select_f,
        t_label=t_label,
        f_label=f_label,
    )


def parse_lt():
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
