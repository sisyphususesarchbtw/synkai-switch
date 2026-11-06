import sqlite3
import pytest
from synkai.bridge import BridgeState
from synkai.workflow import WorkflowState
from synkai.store import Store


@pytest.mark.parametrize('owner,method',[(BridgeState,'db'),(WorkflowState,'db'),(Store,'_connect')])
def test_each_database_scope_releases_its_connection(tmp_path,owner,method):
    state=owner(tmp_path/'state.sqlite')
    with getattr(state,method)() as connection:
        assert connection.execute('SELECT 1').fetchone()[0]==1
    with pytest.raises(sqlite3.ProgrammingError,match='closed'):
        connection.execute('SELECT 1')
