from ductile.pipe.internal import Pipeable, pipe, V, F, L, P, Positions, HERE
import pytest

def test_pipeable_is_iterable():
    assert tuple(Pipeable((0, 1, 2))) == (0, 1, 2)
    assert tuple(Pipeable.of_value('a')) == ('a',)

def test_pipeables_only_pipe_pipeables():
    assert tuple(Pipeable.of_value('foo') | Pipeable.of_value('bar')) == ('foo', 'bar')

    # somewhat weak, since we cannot test every case.
    with pytest.raises(ValueError):
        Pipeable.of_value('foo') | 'bar'
    with pytest.raises(ValueError):
        'bar' | Pipeable.of_value('foo')

def test_piped_pipeables_chain_their_sequences():
    assert tuple(Pipeable((0, 1, 2)) | Pipeable((3, 4, 5))) == (0, 1, 2, 3, 4, 5)

def test_pipeable_of_value_wraps_value_in_a_tuple():
    pipeable = Pipeable.of_value('a')
    assert pipeable.sequence == ('a',)

VALUE = object()
ARGS = ('1', '2')
KWARGS = {'a': 1, 'b': 2}
FN = lambda *args, **kwargs: (args, kwargs)

def test_V():
    result = V(VALUE)
    assert isinstance(result, Pipeable)
    assert tuple(result) == ((Positions.VALUE, VALUE),)

def test_F():
    result_F = F(FN, *ARGS, **KWARGS)
    assert isinstance(result_F, Pipeable)
    assert tuple(result_F) == ((Positions.FIRST, FN, ARGS, KWARGS),)

def test_pipe_F():
    assert pipe(V(VALUE) | F(FN, *ARGS, **KWARGS)) == ((VALUE, *ARGS), KWARGS)

def test_L():
    result_L = L(FN, *ARGS, **KWARGS)
    assert isinstance(result_L, Pipeable)
    assert tuple(result_L) == ((Positions.LAST, FN, ARGS, KWARGS),)

def test_pipe_L():
    assert pipe(V(VALUE) | L(FN, *ARGS, **KWARGS)) == ((*ARGS, VALUE), KWARGS)

def test_P():
    result_P = P(FN, *ARGS, **KWARGS)
    assert isinstance(result_P, Pipeable)
    assert tuple(result_P) == ((Positions.PLACEHOLDER, FN, ARGS, KWARGS),)

def test_pipe_P():
    assert pipe(V(VALUE)
                | P(FN, 1, HERE, 2, **KWARGS)) == ((1, VALUE, 2), KWARGS)
    assert pipe(V(VALUE)
                | P(FN, *ARGS, foo=HERE, bar=True)) == (ARGS, {'foo': VALUE, 'bar': True})
    assert pipe(V(VALUE)
                | P(FN, 1, HERE, HERE, foo=HERE, bar=HERE)) == ((1, VALUE, VALUE), {'foo': VALUE, 'bar': VALUE})

def test_pipe_multiple():
    assert pipe(
        V(VALUE)
        | F(FN, *ARGS, **KWARGS)
        | L(FN, *ARGS, **KWARGS)
        | P(FN, 1, HERE, 2, **KWARGS)
    ) == ((1, ((*ARGS, ((VALUE, *ARGS), KWARGS)), KWARGS), 2), KWARGS)