"""
Parses Jack files into an XML representation
"""
import os
import os.path as path

from tokenizer import tokenize
from jack_parser import Parser
from code_generator import CodeGenerator


def main(input_node):
    if path.isdir(input_node):
        input_files = [
            path.join(input_node, f) for f in os.listdir(input_node) 
            if f.lower().endswith('.jack')
        ]
    elif path.isfile(input_node) and input_node.lower().endswith('.jack'):
        input_files = [input_node]
    else:
        raise ValueError('{} is not a valid file or directory'.format(input_node))

    for filename in input_files:
        print 'Compiling {}'.format(filename)
        output_filename = filename[:-4] + 'vm'
        with open(filename, 'r') as f:
            file_text = f.read()
        file_vm_text = compile(file_text)
        with open(output_filename, 'w') as f:
            f.write(file_vm_text)

def compile(file_text):
    tokens = tokenize(file_text)
    parse_tree = Parser(tokens).parse_class()
    vm_text = CodeGenerator().compile_class(parse_tree)
    return vm_text


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    args = parser.parse_args()
    main(args.target)