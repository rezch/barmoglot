import sys

REGISTER = None
STACK = []
QUEUE = []
#STACK_BORDER = 0

IN_GOTO = []

FUNC_TABLE = {}
IN_FUNC = False

STEP = False

OUTPUT_LOG = []

stack_open = False
queue_open = False
register_open = False


class CodeFileError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'CodeFileError, {}'.format(self.message)
        return 'CodeFileError, check code source file'
        

def InterpreterError(index=None, msg=None):
    print('InterpreterError')
    if index is not None:
        print(f'at symbol: {index}\n')
    if msg is not None:
        print(f'Traceback: {msg}')
    exit(1)


def arg_parse(source=None):
    global STEP
    args = sys.argv
    data = {
        'file': None,
        'stack': False,
        'queue': False,
        'register': False,
        'input': False,
    }

    if '-f' in args:
        try:
            file_index = args.index('-f') + 1
            data['file'] = args[file_index]
        except IndexError:
            raise CodeFileError()
    elif source is None:
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
        STEP = True

    return data


def refactor(file_text):
    return file_text.replace('\n', '').replace('\t', '').replace(' ', '')


def com(command, i, SKIP):
    global REGISTER, STACK, QUEUE, IN_GOTO

    if command == '#':
        REGISTER *= 10
    elif command == '_':
        REGISTER /= 10
    elif command == '!':
        REGISTER = 1 if REGISTER is None else None
    elif command == '.':
        OUTPUT_LOG.append(REGISTER)
        print(REGISTER, end='')
        REGISTER = None
    elif command == '?':
        REGISTER = int(input())
    elif command == '[':
        if len(STACK) == 0:
            REGISTER = None
        else:
            REGISTER = STACK.pop()
    elif command == ']':
        STACK.append(REGISTER)
    elif command == '{':
        if len(QUEUE) == 0:
            REGISTER = None
        else:
            REGISTER = QUEUE.pop(0)
    elif command == '}':
        QUEUE.append(REGISTER)
    elif command == '~':
        stack_upper = STACK.pop()
        reg_val = REGISTER
        REGISTER = stack_upper
        STACK.append(reg_val)
    elif command == "'":
        REGISTER = None
    elif command == '(':
        if REGISTER is None:
            SKIP = True
            return (i, SKIP)
        IN_GOTO.append(i)
    elif command == ')':
        if SKIP:
            SKIP = False
            return (i, SKIP)
        if REGISTER is None:
            IN_GOTO.pop()
            return (i, SKIP)
        i = IN_GOTO[-1]

    return (i, SKIP)


def operator_execute(operand):
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
        REGISTER = 1 if STACK.pop() > REGISTER else None
    elif operand == '>':
        REGISTER = 1 if STACK.pop() < REGISTER else None
    elif operand == '=':
        REGISTER = 1 if STACK.pop() == REGISTER else None
    elif operand == '&':
        if STACK.pop() is not None and REGISTER is not None:
            REGISTER = 1
        else:
            REGISTER = None
    elif operand == '|':
        if STACK.pop() is not None or REGISTER is not None:
            REGISTER = 1
        else:
            REGISTER = None


com_list = ['#', '_', '!', '.', '?', '[', ']', '{', '}', '~', '(', ')', '"', "'"]
operators_list = ['+', '-', '*', '/', '%', '<', '>', '=', '&', '|']
func_com_list = ['^', '$', ':', ';']
'''
    sym: a-z 0-9 @(=space)
    loop(jumper): ()
    func: ^name - implementation, $name - call
'''


def read_func_name(code, index):
    func_name = ''
    while True:
        sym = code[index]
        if sym in com_list or sym in operators_list or sym in func_com_list or sym.isdigit() or sym == '@':
            break
        func_name += sym
        index += 1
    return (func_name, index)


def interp(code, index=0):
    global REGISTER, STACK, QUEUE, STEP, FUNC_TABLE, IN_FUNC
    SKIP = False
    depth = 0
    func_reading = False
    while True:
        sym = code[index]

        if SKIP and not func_reading:
            if sym == '(':
                depth += 1
            elif sym == ')':
                depth -= 1
                SKIP = bool(depth >= 0)
        else:
            if sym == '"':
                break                

            if sym == ';':
                if IN_FUNC:
                    return
                elif not func_reading:
                    InterpreterError(index, 'unexpected found ";" outside the end of the function declaration')
                func_reading = False
                index += 1
                continue

            if func_reading:
                index += 1
                continue

            if sym == '$': # func call
                func_name, index = read_func_name(code, index + 1)
                if func_name not in FUNC_TABLE:
                    InterpreterError(index, f'no such function named {func_name}')
                IN_FUNC = True
                interp(code, FUNC_TABLE[func_name])
                IN_FUNC = False
                continue

            elif sym == '^': # reading the new func implementation
                func_name, index = read_func_name(code, index + 1)

                if code[index] != ':':
                    bad_sym_index = len(func_name)
                    while code[index] != ':':
                        func_name += code[index]
                        index += 1
                    InterpreterError(index, f'unsuitable function name <{func_name}>\n' + '_' * (37 + bad_sym_index) + '^')
                
                if func_name in FUNC_TABLE:
                    InterpreterError(index, f'redefinition of a function <{func_name}>')
                
                FUNC_TABLE[func_name] = index + 1
                func_reading = True
                index += 1
                continue

            elif sym.isdigit():
                REGISTER = int(sym)

            elif sym in com_list:
                index, SKIP = com(sym, index, SKIP)

            elif sym in operators_list:
                operator_execute(sym)

            elif sym == '@':
                REGISTER = ' '

            else:
                REGISTER = sym
        if STEP:
            print("\n---------------------------------")
            print(code[index])
            print("REGISTER: ", REGISTER if REGISTER is not None else '[BARMALEY]')
            print("STACK: ", STACK)
            print("QUEUE: ", QUEUE)
            input()
        index += 1

def parse(file_name, file_input):
    global stack_open, queue_open, register_open
    parsedcode = ""
    try:
        with open(file_name, 'r') as f:
            parsedcode = f.read()
    except FileExistsError or FileNotFoundError:
        raise CodeFileError()
    
    #if '?' in parsedcode and file_input is None:
    #    INPUT_QUEUE = input().split()
    #    INPUT_QUEUE = [int(val) if val.isdigit() else val for val in INPUT_QUEUE]
    return parsedcode


def cout():
    global stack_open, queue_open, register_open
    
    if __name__ != "__main__":
        return 0
    
    if register_open or stack_open or queue_open:
        print("\n---------------------------------")
    if register_open:
        print("REGISTER: ", REGISTER if REGISTER is not None else '[BARMALEY]')

    if stack_open:
        print("STACK: ", STACK)

    if queue_open:
        print("QUEUE: ", QUEUE)


def start(source=None, inp=None):
    global stack_open, queue_open, register_open
    args = arg_parse(source)

    file = args['file'] if source is None else source
    stack_open = args['stack']
    queue_open = args['queue']
    register_open = args['register']

    parse_code = parse(file, inp)
    parse_code = refactor(parse_code)

    interp(parse_code)
    print()

    cout()


if __name__ == "__main__":
    start()
    
