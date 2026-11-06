import pytest
from synkai.lease import RuntimeLease


def test_two_supervisors_cannot_consume_the_same_room_and_budget(tmp_path):
    path=tmp_path/'runtime.lock'
    with RuntimeLease(path):
        with pytest.raises(RuntimeError,match='already running'):
            with RuntimeLease(path):
                pytest.fail('A second supervisor acquired the same state')
    with RuntimeLease(path):
        assert path.exists()
