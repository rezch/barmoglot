import sys


REGISTER = None
STACK = []
QUEUE = []


class CodeFileError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'CodeFileError, {}'.format(self.message)
        else:
            return 'CodeFileError, check code source file'


def arg_parse():
    args = sys.argv
    data = {
        'file': None,
        'stack': False,
        'queue': False,
        'register': False
    }
    
    if '-f' in args:
        try:
            file_index = args.index('-f') + 1
            data['file'] = args[file_index]
        except IndexError:
            raise CodeFileError()
    else:
        raise CodeFileError('select the executive file')

    if '-stack' in args:
        data['stack'] = True
        
    if '-queue' in args:
        data['queue'] = True

    if '-register' in args:
        data['register'] = True
        
    if '-data' in args:
        data['register'] = True
        data['stack'] = True
        data['queue'] = True
        
    return data


def refactor(code):
    return code.replace('\n', '').replace('\t', '').replace(' ', '')


def com(command):
    global REGISTER, STACK, QUEUE
    if command == '#':
        REGISTER *= 10
    elif command == '_':
        REGISTER /= 10
    elif command == '!':
        REGISTER = 1 if REGISTER is None else None
    elif command == '.':
        print(REGISTER, end='')
        REGISTER = None
    elif command == '?':
        REGISTER = input()
        if REGISTER.isdigit():
            REGISTER = int(REGISTER)
    elif command == '[':
        REGISTER = STACK.pop()
    elif command == ']':
        STACK.append(REGISTER)
    elif command == '{':
        REGISTER = QUEUE.pop(0)
    elif command == '}':
        QUEUE.append(REGISTER)
    elif command == '~':
        stack_upper = STACK.pop()
        reg_val = REGISTER
        REGISTER = stack_upper
        STACK.append(reg_val)


def oper(operand):
    global REGISTER, STACK, QUEUE
    if operand == '+':
        REGISTER = STACK.pop() + REGISTER
    elif operand == '-':
        REGISTER = STACK.pop() - REGISTER
    elif operand == '*':
        REGISTER = STACK.pop() * REGISTER
    elif operand == '/':
        REGISTER = STACK.pop() / REGISTER
    elif operand == '%':
        REGISTER = STACK.pop() % REGISTER
    elif operand == '<':
        REGISTER = int(STACK.pop() < REGISTER)
    elif operand == '>':
        REGISTER = int(STACK.pop() > REGISTER)
    elif operand == '=':
        REGISTER = int(STACK.pop() == REGISTER)
    elif operand == '&':
        if STACK.pop() != None and REGISTER != None:
            REGISTER = 1
        else:
            REGISTER = None
    elif operand == '|':
        if STACK.pop() != None or REGISTER != None:
            REGISTER = 1
        else:
            REGISTER = None


com_list = ['#', '_', '!', '.', '?', '[]', '{}', '~']
oper_list = ['+', '-', '*', '/', '%', '<', '>', '=', '&', '|']
'''sym: a-z 0-9 @(=space)
func: ()'''
def interp(code):
    global REGISTER, STACK, QUEUE
    i = 0
    while True:
        sym = code[i]
        if sym == '"':
            break
        elif sym.isdigit():
            REGISTER = int(sym)
        elif sym in com_list:
            com(sym)
        elif sym in oper_list:
            oper(sym)
        elif sym == '(':
            pass
        elif sym == ')':
            pass
        elif sym == '@':
            REGISTER = ' '
        else:
            REGISTER = sym
        i += 1



args = arg_parse()

file = args['file']
stack_open = args['stack']
queue_open = args['queue']
register_open = args['register']


code = ""
try:
    with open(file, 'r') as f:
        code = f.read()
except FileExistsError or FileNotFoundError:
    raise CodeFileError()

code = refactor(code)

interp(code)

print("\n---------------------------------")
if register_open:
    print("REGISTER: ", REGISTER)

if stack_open:
    print("STACK: ", STACK)
    
if queue_open:
    print("QUEUE: ", QUEUE)
