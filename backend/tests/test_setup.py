from synkai.setup import local_environment, operator_identity, verified_compose
import pytest


def test_generated_credentials_survive_repeated_setup(tmp_path):
    first=local_environment(tmp_path)
    second=local_environment(tmp_path)
    assert first==second
    assert first['SWITCH_BIND_ADDR']=='127.0.0.1'
    assert first['SECRET_KEYS'].startswith('primary:')
    assert len(first['GATEWAY_ADMIN_PASSWORD'])>=32
    assert first['GATEWAY_ADMIN_PASSWORD']!=first['MATTERMOST_USER_PASSWORD']


def test_operator_is_derived_only_from_the_linked_bridge_identity():
    identities=[{'bridge_id':'other','external_username':'wrong'}, {'bridge_id':'bridge-1','external_username':'operator'}]
    assert operator_identity(identities,'bridge-1')=='@switch-mattermost-bridge-1-operator:localhost'
    with pytest.raises(ValueError,match='linked'):
        operator_identity(identities,'missing')


def test_unexpected_downloaded_stack_is_rejected():
    with pytest.raises(ValueError,match='digest'):
        verified_compose(b'not the pinned official stack')
