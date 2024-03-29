from ductile.pipe.internal import Pipeable, pipe, V, F, L, P, Positions, HERE
import pytest

def test_pipeable_is_iterable():
    assert tuple(Pipeable((0, 1, 2))) == (0, 1, 2)
    assert tuple(Pipeable.of_value('a')) == ('a',)

def test_pipeables_only_pipe_pipeables():
    assert tuple(Pipeable.of_value('foo') | Pipeable.of_value('bar')) == ('foo', 'bar')

    # somewhat weak, since we cannot test every case.
    with pytest.raises(ValueError, match='You can only pipe a Pipeable into a Pipeable'):
        Pipeable.of_value('foo') | 'bar'
    with pytest.raises(ValueError, match='You can only pipe a Pipeable into a Pipeable'):
        'bar' | Pipeable.of_value('foo')

def test_piped_pipeables_chain_their_sequences():
    assert tuple(Pipeable((0, 1, 2)) | Pipeable((3, 4, 5))) == (0, 1, 2, 3, 4, 5)

def test_pipeable_of_value_wraps_value_in_a_tuple():
    pipeable = Pipeable.of_value('a')
    assert pipeable.sequence == ('a',)

VALUE = object()
ARGS = (object(), object())
KWARGS = {'a': object(), 'b': object()}
FN = lambda *args, **kwargs: (args, kwargs)

def test_V():
    result = V(VALUE)
    assert isinstance(result, Pipeable)
    assert tuple(result) == ((Positions.VALUE, VALUE),)

def test_F():
    assert isinstance(F(FN, *ARGS, **KWARGS), Pipeable)
    assert tuple(F(FN, *ARGS, **KWARGS)) == ((Positions.FIRST, FN, ARGS, KWARGS),)
    assert tuple(F(FN, *ARGS)) == ((Positions.FIRST, FN, ARGS, {}),)
    assert tuple(F(FN)) == ((Positions.FIRST, FN, (), {}),)

def test_pipe_F():
    assert pipe(V(VALUE) | F(FN, *ARGS, **KWARGS)) == ((VALUE, *ARGS), KWARGS)

def test_L():
    assert isinstance(L(FN, *ARGS, **KWARGS), Pipeable)
    assert tuple(L(FN, *ARGS, **KWARGS)) == ((Positions.LAST, FN, ARGS, KWARGS),)
    assert tuple(L(FN, *ARGS)) == ((Positions.LAST, FN, ARGS, {}),)
    assert tuple(L(FN)) == ((Positions.LAST, FN, (), {}),)

def test_pipe_L():
    assert pipe(V(VALUE) | L(FN, *ARGS, **KWARGS)) == ((*ARGS, VALUE), KWARGS)

def test_P():
    assert isinstance(P(FN, *ARGS, **KWARGS), Pipeable)
    assert tuple(P(FN, *ARGS, **KWARGS)) == ((Positions.PLACEHOLDER, FN, ARGS, KWARGS),)
    assert tuple(P(FN, *ARGS)) == ((Positions.PLACEHOLDER, FN, ARGS, {}),)
    assert tuple(P(FN)) == ((Positions.PLACEHOLDER, FN, (), {}),)

def test_pipe_P():
    assert pipe(V(VALUE)
                | P(FN, 1, HERE, 2, **KWARGS)) == ((1, VALUE, 2), KWARGS)
    assert pipe(V(VALUE)
                | P(FN, *ARGS, foo=HERE, bar=True)) == (ARGS, {'foo': VALUE, 'bar': True})
    assert pipe(V(VALUE)
                | P(FN, 1, HERE, HERE, foo=HERE, bar=HERE)) == ((1, VALUE, VALUE), {'foo': VALUE, 'bar': VALUE})

def test_pipeline():
    assert pipe(
        V(VALUE)
        | F(FN, *ARGS)
        | L(FN, *ARGS, **KWARGS)
        | P(FN, 1, HERE, 2, **KWARGS)
    ) == ((1, ((*ARGS, ((VALUE, *ARGS), {})), KWARGS), 2), KWARGS)

def test_wrong_instruction_exceptions_raised():
    with pytest.raises(TypeError, match=r'missing \d+ required positional argument'):
        pipe()

    with pytest.raises(ValueError, match='First expression must be a value.'):
        pipe((1,))
    
    with pytest.raises(ValueError, match='Incorrect instruction format.'):
        pipe(((Positions.VALUE, VALUE),
              (Positions.FIRST, FN)))

    with pytest.raises(NotImplementedError):
        pipe(((Positions.VALUE, VALUE),
              (0.1, FN, ARGS, KWARGS)))

    with pytest.raises(ValueError, match='Values only allowed as the first expression.'):
        pipe(((Positions.VALUE, VALUE),
              (Positions.FIRST, FN, ARGS, KWARGS),
              (Positions.VALUE, VALUE)))