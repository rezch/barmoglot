import sys


REGISTER = None
STACK = []
QUEUE = []

INGOTO = []
SKIP = False

INPUT_QUEUE = []
STEP = False


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
        'register': False,
        'input': False,
        'step': False
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
    if '-step' in args:
        data['step'] = True
        
    return data


def refactor(code):
    return code.replace('\n', '').replace('\t', '').replace(' ', '')


def com(command, i):
    global REGISTER, STACK, QUEUE, INGOTO, SKIP, INPUT_QUEUE
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
        if INPUT_QUEUE != []:
            REGISTER = INPUT_QUEUE.pop(0)
        else:
            REGISTER = None
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
    elif command == '(':
        if REGISTER == None:
            SKIP = True
            return i
        INGOTO.append(i)
    elif command == ')':
        if SKIP == True:
            SKIP = False
            return i
        if REGISTER == None:
            INGOTO.pop()
            return i
        i = INGOTO[-1]

    return i
        


def oper(operand):
    global REGISTER, STACK, QUEUE
    if operand == '+':
        REGISTER = STACK.pop() + REGISTER
    elif operand == '-':
        REGISTER = REGISTER - STACK.pop()
    elif operand == '*':
        REGISTER = STACK.pop() * REGISTER
    elif operand == '/':
        REGISTER = REGISTER / STACK.pop()
    elif operand == '%':
        REGISTER = REGISTER % STACK.pop()
    elif operand == '<':
        REGISTER = int(STACK.pop() > REGISTER)
    elif operand == '>':
        REGISTER = int(STACK.pop() < REGISTER)
    elif operand == '=':
        REGISTER = 1 if STACK.pop() == REGISTER else None
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


com_list = ['#', '_', '!', '.', '?', '[', ']', '{', '}', '~', '(', ')']
oper_list = ['+', '-', '*', '/', '%', '<', '>', '=', '&', '|']
'''sym: a-z 0-9 @(=space)
func: ()'''
def interp(code):
    global REGISTER, STACK, QUEUE, SKIP, STEP
    i = 0
    depth = 0
    while True:
        sym = code[i]
        if SKIP:
            if sym == '(':
                depth += 1
            elif sym == ')':
                depth -= 1
                SKIP = bool(depth >= 0)
        else:
            if sym == '"':
                break
            elif sym.isdigit():
                REGISTER = int(sym)
            elif sym in com_list:
                i = com(sym, i)
            elif sym in oper_list:
                oper(sym)
            elif sym == '@':
                REGISTER = ' '
            else:
                REGISTER = sym
        if STEP:
            print("\n---------------------------------")
            print(code[i])
            print("REGISTER: ", REGISTER if REGISTER is not None else '[BARMALEY]')
            print("STACK: ", STACK)
            print("QUEUE: ", QUEUE)
            input()
        i += 1



args = arg_parse()

file = args['file']
stack_open = args['stack']
queue_open = args['queue']
register_open = args['register']
STEP = args['step']


code = ""
try:
    with open(file, 'r') as f:
        code = f.read()
except FileExistsError or FileNotFoundError:
    raise CodeFileError()

if '?' in code:
    INPUT_QUEUE = input().split()
    INPUT_QUEUE = [int(val) if val.isdigit() else val for val in INPUT_QUEUE]

code = refactor(code)

interp(code)

if register_open or stack_open or queue_open:
    print("\n---------------------------------")
if register_open:
    print("REGISTER: ", REGISTER if REGISTER is not None else '[BARMALEY]')

if stack_open:
    print("STACK: ", STACK)
    
if queue_open:
    print("QUEUE: ", QUEUE)
