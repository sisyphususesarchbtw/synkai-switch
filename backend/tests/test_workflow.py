import pytest

from synkai.workflow import WorkflowState


def approval(sender='operator', body='@synkai-verifier approve case-01', kind='user', room='room'):
    return {'room_id':room,'payload':{'addressed':True,'sender':sender,'sender_kind':kind,
        'message_id':'approval-message','body':body}}


def setup(tmp_path):
    state=WorkflowState(tmp_path/'workflow.sqlite')
    state.propose('case-01', room_id='room', operator_ids=['operator'], base='base', check_hash='frozen', report_id='report')
    return state


@pytest.mark.parametrize('event', [approval(sender='fixer',kind='agent'), approval(body='> approve case-01'),
    approval(body='The user said approve case-01'),approval(room='other'),approval(kind='agent')])
def test_agent_quotes_and_other_rooms_cannot_approve(tmp_path,event):
    state=setup(tmp_path)
    assert state.approve('case-01',event,current_check='frozen') is False
    assert state.get('case-01')['status']=='NEEDS_APPROVAL'


def test_real_operator_approval_is_bound_to_exact_check_and_message(tmp_path):
    state=setup(tmp_path)
    assert state.approve('case-01',approval(),current_check='frozen')
    case=state.get('case-01')
    assert case['approval_message_id']=='approval-message'
    assert case['approved_by']=='operator'
    assert state.approve('case-01',approval(),current_check='frozen') is False


def test_changed_check_requires_a_new_proposal(tmp_path):
    state=setup(tmp_path)
    assert state.approve('case-01',approval(),current_check='changed') is False


def test_interrupted_coding_requires_a_new_operator_retry_without_resetting_budget(tmp_path):
    state=setup(tmp_path)
    state.approve('case-01',approval(),current_check='frozen')
    state.reserve_attempt('case-01')
    state.recover_interrupted()
    restored=state.get('case-01')
    assert restored['status']=='INCONCLUSIVE'
    assert restored['attempts']==1
    with pytest.raises(ValueError): state.reserve_attempt('case-01')
    assert 'interrupted' in restored['error'].lower()


def test_coding_attempt_budget_survives_restart_and_stops_after_one_repair(tmp_path):
    state=setup(tmp_path)
    state.approve('case-01',approval(),current_check='frozen')
    assert state.reserve_attempt('case-01')==1
    with pytest.raises(ValueError):
        state.reserve_attempt('case-01')
    state.update('case-01',status='REJECTED')
    state=WorkflowState(tmp_path/'workflow.sqlite')
    assert state.reserve_attempt('case-01')==2
    state.update('case-01',status='REJECTED')
    with pytest.raises(ValueError):
        state.reserve_attempt('case-01')


def test_environment_failure_retry_requires_operator_and_keeps_attempt_count(tmp_path):
    state=setup(tmp_path)
    state.approve('case-01',approval(),current_check='frozen')
    state.reserve_attempt('case-01')
    state.update('case-01',status='INCONCLUSIVE',error='nested shell unavailable')
    assert not state.authorize_retry('case-01',approval(sender='agent',body='retry case-01',kind='agent'),current_check='frozen')
    assert state.authorize_retry('case-01',approval(body='@synkai-verifier retry case-01'),current_check='frozen')
    assert state.get('case-01')['previous_errors']==['nested shell unavailable']
    assert state.reserve_attempt('case-01')==2
