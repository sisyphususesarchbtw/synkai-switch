import pytest
from pydantic import ValidationError

from synkai.settings import Settings


def test_runtime_settings_do_not_serialize_keys(tmp_path):
    config = Settings(switch_url='http://127.0.0.1:8791', room_id='room',
        operator_ids=['operator'], repo_root=tmp_path, verifier_id='verifier',
        verifier_key='verifier-secret', fixer_id='fixer', fixer_key='fixer-secret')
    assert 'verifier-secret' not in config.model_dump_json()
    assert 'fixer-secret' not in repr(config)


def test_empty_operator_allowlist_cannot_start_a_live_workflow(tmp_path):
    with pytest.raises(ValidationError):
        Settings(switch_url='http://127.0.0.1:8791', room_id='room', operator_ids=[],
            repo_root=tmp_path, verifier_id='verifier', verifier_key='key', fixer_id='fixer', fixer_key='key')
