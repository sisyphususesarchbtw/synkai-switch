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
