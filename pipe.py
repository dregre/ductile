import types
from typing import Any
from itertools import chain
from functools import reduce

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
    
class Pipeable(tuple):
    @classmethod
    def of_value(cls, val):
        return cls((val,))

    def __ror__(self, other):
        if isinstance(other, Pipeable):
            return Pipeable(chain(other, self))
        else:
            return Pipeable.of_value(other) | self
        
    def __or__(self, other):
        if isinstance(other, Pipeable):
            return Pipeable(chain(self, other))
        else:
            return self | Pipeable.of_value(other)
    
def f(fn, *args, **kwargs):
    return Pipeable.of_value((1, fn, args, kwargs))

def b(fn, *args, **kwargs):
    return Pipeable.of_value((-1, fn, args, kwargs))
    
def handle_fn_and_args(val, fn_and_args):
        order, fn, args, kwargs = fn_and_args
        newargs = chain([val], args) if order == 1 else chain(args, [val])
        return fn(*newargs, **kwargs)

def pipe(val_and_fns_and_args):
    val, *fns_and_args = val_and_fns_and_args
    return reduce(handle_fn_and_args, fns_and_args, val)