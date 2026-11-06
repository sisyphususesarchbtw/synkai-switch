from fastapi.testclient import TestClient
from synkai.api import create_app
from synkai.runner import DockerRunner


def client(tmp_path):
    return TestClient(create_app(data_dir=tmp_path, runner=DockerRunner(binary=str(tmp_path / "missing"))), base_url="http://localhost")


def test_unavailable_runner_is_honest_and_no_cases_are_fabricated(tmp_path):
    with client(tmp_path) as app:
        state = app.get("/api/state").json()
        assert state["runner"]["ready"] is False
        assert state["cases"] == []
        assert state["switch"]["connected"] is False


def test_foreign_site_cannot_create_or_run_cases(tmp_path):
    with client(tmp_path) as app:
        app.get("/api/state")
        assert app.post("/api/demo", headers={"Origin": "https://attacker.example"}).status_code == 403


def test_post_without_session_is_rejected(tmp_path):
    with client(tmp_path) as app:
        assert app.post("/api/demo", headers={"Origin": "http://localhost:8787"}).status_code == 403


def test_unknown_case_and_arbitrary_candidate_are_rejected(tmp_path):
    with client(tmp_path) as app:
        app.get("/api/state")
        headers = {"Origin": "http://localhost:8787"}
        assert app.post("/api/cases/unknown/run", json={"candidate": "../../secret"}, headers=headers).status_code in {404,422}


def prepare_live(tmp_path):
    import json
    from synkai.bridge import BridgeState
    from synkai.workflow import WorkflowState
    from synkai.store import Store
    case=Store(tmp_path/'cases.sqlite').create_case('Coupon applies once','base')
    private=tmp_path/'switch'
    private.mkdir(exist_ok=True)
    (private/'runtime-config.json').write_text(json.dumps({'fixer_id':'fixer','verifier_id':'verifier','fixer_key':'never-expose-this-key'}))
    bus=BridgeState(private/'runtime.sqlite')
    for agent in ['fixer','verifier']:
        bus.accept(agent,'room',{'event':'connection_state','data':{'generation':1,'rooms':['room'],'cursor':0}})
    WorkflowState(private/'workflow.sqlite').propose('case',room_id='room',operator_ids=['human'],base='base',
        check_hash='check',report_id='report',ui_case_id=case['id'],source_room_url='http://localhost:8792/room')
    return case


def test_state_projects_real_room_liveness_without_keys(tmp_path):
    prepare_live(tmp_path)
    with client(tmp_path) as app:
        response=app.get('/api/state')
        state=response.json()
        assert state['mode']=='live-switch'
        assert state['switch']['connected'] is True
        assert state['live_case']['source_room_url']=='http://localhost:8792/room'
        assert 'never-expose-this-key' not in response.text


def test_browser_cannot_bypass_room_approval_for_live_case(tmp_path):
    case=prepare_live(tmp_path)
    with client(tmp_path) as app:
        app.get('/api/state')
        response=app.post(f"/api/cases/{case['id']}/run",json={'candidate':'false-fix','revision':0},
            headers={'Origin':'http://localhost:8787'})
        assert response.status_code==409


def test_live_model_count_reports_attempts_instead_of_fixture_zero(tmp_path):
    from synkai.workflow import WorkflowState
    prepare_live(tmp_path)
    WorkflowState(tmp_path/'switch/workflow.sqlite').update('case',attempts=2)
    with client(tmp_path) as app:
        assert app.get('/api/state').json()['model_calls']==2
