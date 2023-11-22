from typing import Any
from itertools import chain

class Pipe:
    def __init__(self, val):
        self.val = val
    
    def __getitem__(self, arg):
        if isinstance(arg, tuple):
            (fn, order) = arg
        else:
            (fn, order) = (arg, 1)
        return PipeCallable(fn, self.eval(), order)
    
    def eval(self):
        return self.val

    def __invert__(self):
        return self.val

class PipeCallable(Pipe):
    def eval(self):
        args = chain([self.val], self.args) if self.order == 1 else chain(self.args, [self.val])
        return self.fn(*args, **self.kwargs)

    def __init__(self, fn, val, order) -> None:
        self.fn = fn
        self.val = val
        self.order = order
        self.args = tuple()
        self.kwargs = dict()
    
    def __invert__(self):
        return self.eval()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.args = args
        self.kwargs = kwargs
        return self