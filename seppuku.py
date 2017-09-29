import os
import signal

def honor(expr, msg=None, level=9):
    """Honorable assertion"""
    if not expr:
        commit(msg=msg, level=level)

def commit(msg=None, level=9):
    print(msg)
    os.kill(os.getpid(), level)

class HonorableError(Exception):
    def __init__(self, msg=None, original_exc=None, level=9):
        if original_exc:
            super(HonorableError, self).__init__(msg)
        else:
            super(HonorableError, self).__init__(msg + ': {}'.format(original_exc))
        import traceback
        traceback.print_exc() # XXX this goes to stderr!
        commit(msg, level=level)