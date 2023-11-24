from itertools import chain
from functools import reduce
from enum import Enum
    
class Pipeable:
    def __init__(self, sequence):
        self.sequence = sequence

    @classmethod
    def of_value(cls, val):
        return cls((val,))

    def __ror__(self, other):
        if isinstance(other, Pipeable):
            return Pipeable(chain(other, self))
        else:
            return self.of_value(other) | self
        
    def __or__(self, other):
        if isinstance(other, Pipeable):
            return Pipeable(chain(self, other))
        else:
            return self | self.of_value(other)
        
    def __iter__(self):
        return self.sequence.__iter__()
    
    def __next__(self):
        return self.sequence.__next__()
    
    def __repr__(self):
        return "<Pipeable: " + tuple(self.sequence).__repr__() + ">"
        
class Positions(int, Enum):
    FRONT = 1
    BACK = 2
    PLACEHOLDER = 3
    
def F(fn, *args, **kwargs):
    return Pipeable.of_value((Positions.FRONT, fn, args, kwargs))

def B(fn, *args, **kwargs):
    return Pipeable.of_value((Positions.BACK, fn, args, kwargs))

def P(fn, *args, **kwargs):
    return Pipeable.of_value((Positions.PLACEHOLDER, fn, args, kwargs))
    
def handle_fn_and_args(val, fn_and_args):
    match fn_and_args:
        case (Positions.FRONT, fn, args, kwargs):
            return fn(*chain([val], args), **kwargs)
        case (Positions.BACK, fn, args, kwargs):
            return fn(*chain(args, [val]), **kwargs)
        case (Positions.PLACEHOLDER, fn, args, kwargs) if Positions.PLACEHOLDER in args:
            return fn(*map(lambda x: val if x is Positions.PLACEHOLDER else x, args), **kwargs)
        case (_, _, _, _):
            raise NotImplementedError(
                "Only piping to the front (prepend) or back (append) "
                "or to a specific placeholder position of *args is "
                "currently supported.")
        case _:
            raise ValueError("Incorrect instruction format.")

def pipe(val_and_fns_and_args):
    val, *fns_and_args = val_and_fns_and_args
    return reduce(handle_fn_and_args, fns_and_args, val)