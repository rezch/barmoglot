from os import system
import barmo


class InputFileError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'InputFileError, {}'.format(self.message)
        else:
            return 'InputFileError, check input source file'


def test(inp) -> list:
    out = []
    
    return out


def testing(inp_file, source):
    inp = ''
    try:
        with open(inp_file, 'r') as f:
            inp = f.read()
    except FileNotFoundError:
        raise InputFileError

    out = test(inp)
    res = barmo.start(filename, inp)

    if out != res:
        print(f'WA on test: {inp} except: {out} found: {res}=')
    else:
        print("OK")


if __name__ == "__main__":
    testing('input.txt', 'code.brm')
        
        

    

