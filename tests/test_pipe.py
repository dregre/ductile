from ductile.pipe.internal import Pipeable
import pytest

def test_pipeables_only_pipe_pipeables():
    assert tuple(Pipeable.of_value('foo') | Pipeable.of_value('bar')) == ('foo', 'bar')

    with pytest.raises(ValueError):
        Pipeable.of_value('foo') | 'bar'
    with pytest.raises(ValueError):
        'bar' | Pipeable.of_value('foo')

