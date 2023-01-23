import sys

REGISTER = None
STACK = []
QUEUE = []

IN_GOTO = []
SKIP = False

INPUT_QUEUE = []
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
        else:
            return 'CodeFileError, check code source file'


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


def com(command, i):
    global REGISTER, STACK, QUEUE, IN_GOTO, SKIP, INPUT_QUEUE
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
        if INPUT_QUEUE:
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
        if REGISTER is None:
            SKIP = True
            return i
        IN_GOTO.append(i)
    elif command == ')':
        if SKIP:
            SKIP = False
            return i
        if REGISTER is None:
            IN_GOTO.pop()
            return i
        i = IN_GOTO[-1]

    return i


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


com_list = ['#', '_', '!', '.', '?', '[', ']', '{', '}', '~', '(', ')']
operators_list = ['+', '-', '*', '/', '%', '<', '>', '=', '&', '|']
'''sym: a-z 0-9 @(=space)
func: ()'''


def interp(code):
    global REGISTER, STACK, QUEUE, SKIP, STEP
    i = 0
    depth = 0
    while True:
        sym = code[i]
        print(sym)
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
            elif sym in operators_list:
                operator_execute(sym)
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

def parse(file_name, file_input):
    global stack_open, queue_open, register_open, INPUT_QUEUE
    parsedcode = ""
    try:
        with open(file_name, 'r') as f:
            parsedcode = f.read()
    except FileExistsError or FileNotFoundError:
        raise CodeFileError()
    
    if '?' in parsedcode and file_input is None:
        INPUT_QUEUE = input().split()
        INPUT_QUEUE = [int(val) if val.isdigit() else val for val in INPUT_QUEUE]
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

    cout()


if __name__ == "__main__":
    start()
    
