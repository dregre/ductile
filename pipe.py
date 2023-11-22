import types
from typing import Any

from itertools import chain

class Pipe:
    def __init__(self, val) -> None:
        self.val = val

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.val

    def __truediv__(self, nextfn):
        if isinstance(nextfn, PipeCallable):
            nextfn.args = chain((self(),), nextfn.args)
            return nextfn
        return PipeCallable(nextfn, (self(),))
    
    def __floordiv__(self, nextfn):
        if isinstance(nextfn, PipeCallable):
            nextfn.args = chain(nextfn.args, (self(),))
            return nextfn
        result = PipeCallable(nextfn)
        result.lastargs = (self(),)
        return result
    
    def __invert__(self):
        return self()

class PipeCallable:
    def __init__(self, fn, args=tuple(), kwargs=dict(), lastargs=tuple()) -> None:
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.lastargs = lastargs

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        val = self.fn(*chain(self.args, args, self.lastargs), **(self.kwargs | kwds))
        self.args = tuple()
        self.kwargs = dict()
        return val
    
    def __mul__(self, other):
        self.args = chain(self.args, other)
        return self
    
    def __mod__(self, other):
        self.kwargs = self.kwargs | other
        return self

    def __truediv__(self, nextfn):
        if isinstance(nextfn, PipeCallable):
            nextfn.args = chain((self(),), nextfn.args)
            return nextfn
        return PipeCallable(nextfn, (self(),))
    
    def __floordiv__(self, nextfn):
        if isinstance(nextfn, PipeCallable):
            nextfn.args = chain(nextfn.args, (self(),))
            return nextfn
        result = PipeCallable(nextfn)
        result.lastargs = (self(),)
        return result
    
    def __invert__(self):
        return self()
        

def pipe(value):
    pass
