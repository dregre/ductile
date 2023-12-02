from ductile.pipe.internal import Pipeable
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