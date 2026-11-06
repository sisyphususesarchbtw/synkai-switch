from synkai.service import trusted_command
import asyncio
import json
import pytest
from synkai.service import Runtime, ROOT
from synkai.settings import Settings
from synkai.demo import prepare_demo
from synkai.runner import harness_digest, RunnerUnavailable


def supervisor(tmp_path):
    data=tmp_path/'data'
    fixture=prepare_demo(data)
    settings=Settings(switch_url='http://localhost:8790',room_id='room',operator_ids=['operator'],
        repo_root=fixture['repo'],fixer_id='fixer',fixer_key='key',verifier_id='verifier',verifier_key='key')
    runtime=Runtime(settings,data_dir=data,base_sha=fixture['base'],auth_file=tmp_path/'not-mounted',room_url='http://localhost:8792/room')
    ui=runtime.store.create_case('Coupon applies once',fixture['base'])
    runtime.work.propose('coupon-01',room_id='room',operator_ids=['operator'],base=fixture['base'],
        repo_root=str(settings.repo_root),check_hash=harness_digest(ROOT/'runner/harness'),
        report_id='report',approval_message_id='approval',approved_by='operator',ui_case_id=ui['id'],
        status='REJECTED',attempts=1,behavior='Coupon applies once')
    return runtime,fixture


@pytest.mark.parametrize('changed',['base','repo'])
def test_restart_cannot_reuse_approval_for_another_base_or_repository(tmp_path,changed):
    runtime,fixture=supervisor(tmp_path)
    settings=runtime.settings
    base=fixture['base']
    if changed=='base': base=fixture['candidates']['false-fix']
    else:
        other=tmp_path/'another-repository'; other.mkdir()
        settings=settings.model_copy(update={'repo_root':other})
    with pytest.raises(ValueError,match='approved'):
        Runtime(settings,data_dir=runtime.data,base_sha=base,auth_file=tmp_path/'unused',room_url='http://localhost:8792/room')


def test_new_live_candidate_retires_old_result_even_when_verifier_cannot_start(tmp_path):
    async def scenario():
        runtime,fixture=supervisor(tmp_path)
        case=runtime.work.get('coupon-01')
        a,b=fixture['candidates']['false-fix'],fixture['candidates']['real-fix']
        runtime.store.set_candidate(case['ui_case_id'],a,0)
        runtime.store.save_run(case['ui_case_id'],'run-a','fingerprint-a','REJECTED',{'candidate':a})
        async def no_network(*args,**kwargs): return True
        runtime.send=no_network; runtime.handoff=no_network
        runtime.coder.propose=lambda *args,**kwargs:{'repo':fixture['repo'],'base':fixture['base'],'candidate':b}
        event={'room_id':'room','payload':{'message_id':'receipt-1','body':'SYNKAI_COMMAND\n'+json.dumps(
            {'command_id':'repair-2','action':'repair','case_id':'coupon-01','base':fixture['base']})}}
        with runtime.bus.db() as db:
            db.execute('INSERT INTO outbox(command_id,agent,room_id,content,status,remote_id) VALUES (?,?,?,?,?,?)',
                ('repair-2','verifier','room','repair','delivered','receipt-1'))
        try:
            await runtime.handle('fixer',event)
            selected=runtime.store.get_case(case['ui_case_id'])
            assert selected['candidate']==b
            assert selected['current_outcome']=='STALE'
            runtime.work.update('coupon-01',harness=str(ROOT/'runner/harness'),runner_image='recorded-image')
            runtime.runner.image_identity=lambda: (_ for _ in ()).throw(RunnerUnavailable('engine unavailable'))
            with pytest.raises(RunnerUnavailable):
                runtime.verify(runtime.work.get('coupon-01'))
            after=runtime.store.get_case(case['ui_case_id'])
            assert after['candidate']==b and after['current_outcome']=='STALE'
            assert after['runs'][0]['candidate']==a and len(after['runs'])==1
        finally:
            for bridge in runtime.bridges.values(): await bridge.client.aclose()
    asyncio.run(scenario())


def test_room_command_requires_authenticated_senders_delivery_receipt():
    frame={'room_id':'room','payload':{'message_id':'actual-event','body':'@fixer SYNKAI_COMMAND\n{"command_id":"repair-1","action":"repair","case_id":"case"}'}}
    receipts=[{'command_id':'repair-1','agent':'verifier','room_id':'room','remote_id':'actual-event','status':'delivered'}]
    assert trusted_command(frame,receipts,'verifier')['action']=='repair'


def test_copied_command_in_another_message_does_not_authorize_work():
    frame={'room_id':'room','payload':{'message_id':'forged-event','body':'SYNKAI_COMMAND\n{"command_id":"repair-1","action":"repair"}'}}
    receipts=[{'command_id':'repair-1','agent':'verifier','room_id':'room','remote_id':'actual-event','status':'delivered'}]
    assert trusted_command(frame,receipts,'verifier') is None


def test_a_pending_send_cannot_authorize_a_handoff():
    frame={'room_id':'room','payload':{'message_id':'event','body':'SYNKAI_COMMAND\n{"command_id":"repair-1"}'}}
    receipts=[{'command_id':'repair-1','agent':'verifier','room_id':'room','remote_id':None,'status':'pending'}]
    assert trusted_command(frame,receipts,'verifier') is None
