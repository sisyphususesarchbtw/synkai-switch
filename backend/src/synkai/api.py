"""Local evidence service. Controlled fixtures are labelled; live agents are not simulated."""
import hashlib
import json
import os
import secrets
import threading
import time
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .demo import export_snapshot, prepare_demo
from .runner import DockerRunner, RunnerUnavailable, freeze_harness, harness_digest
from .store import Conflict, Store
from .verification import classify

ROOT = Path(__file__).resolve().parents[3]


class RunRequest(BaseModel):
    candidate: Literal["false-fix", "real-fix"]
    revision: int = Field(ge=0)


def create_app(data_dir: Path | None = None, runner: DockerRunner | None = None) -> FastAPI:
    data_dir = data_dir or ROOT / ".local"
    data_dir.mkdir(parents=True, exist_ok=True)
    store, runner = Store(data_dir / "cases.sqlite"), runner or DockerRunner()
    app = FastAPI(title="Synkai", docs_url="/api/docs", redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
    secret = secrets.token_urlsafe(32)
    lock = threading.Lock()
    job: dict = {}
    probe: dict = {"at": 0, "value": {"ready": False, "message": "Checking engine"}}
    allowed_origins = {"http://localhost:8787", "http://127.0.0.1:8787", "http://localhost:5173", "http://127.0.0.1:5173"}

    def authorize(request: Request):
        if request.headers.get("origin") not in allowed_origins or not secrets.compare_digest(request.cookies.get("synkai_session", ""), secret):
            raise HTTPException(403, "Open the local Synkai app before performing this action.")

    def runner_status():
        if time.monotonic() - probe["at"] > 8:
            probe.update(at=time.monotonic(), value=runner.status())
        return probe["value"]

    @app.get("/health")
    def health():
        return {"service": "synkai", "version": "0.1.0", "runner": runner_status()}

    @app.get("/api/state")
    def state(response: Response):
        response.set_cookie("synkai_session", secret, httponly=True, samesite="strict")
        response.headers["Cache-Control"] = "no-store"
        manifest = data_dir / "demo.json"
        demo = json.loads(manifest.read_text()) if manifest.exists() else None
        status = runner_status()
        try:
            image = runner.image_identity() if status["ready"] else None
        except RunnerUnavailable:
            image = None
        try:
            current_harness = harness_digest(ROOT / "runner" / "harness")
        except OSError:
            current_harness = None
        current_inputs = {"harness": current_harness, "image": image}
        return {"cases": store.list_cases(current_inputs), "runner": status, "job": dict(job),
                "switch": {"connected": False, "message": "No live Switch session is connected yet"},
                "candidates": demo["candidates"] if demo else {}, "mode": "controlled-fixture",
                "model_calls": 0, "cost": None}

    @app.post("/api/demo", dependencies=[Depends(authorize)])
    def demo():
        with lock:
            existing = store.list_cases()
            if existing:
                return existing[0]
            try:
                fixture = prepare_demo(data_dir)
                return store.create_case("A 10% coupon on a 10000-cent cart must leave 9000 cents. Apply the coupon exactly once.", fixture["base"])
            except (ValueError, OSError) as exc:
                raise HTTPException(409, "Fixture setup is incomplete. Inspect the local fixture repository.") from exc

    def execute(case_id: str, run_id: str, candidate: str, fixture: dict, image: str):
        started = time.monotonic()
        evidence = {"candidate": candidate, "base": fixture["base"], "image": image,
                    "fixture": True, "model_calls": 0, "stages": []}
        outcome = "INCONCLUSIVE"
        fingerprint = ""
        try:
            run_dir = data_dir / "runs" / run_id
            base_dir, candidate_dir = run_dir / "original", run_dir / "candidate"
            export_snapshot(Path(fixture["repo"]), fixture["base"], base_dir)
            export_snapshot(Path(fixture["repo"]), candidate, candidate_dir)
            harness = run_dir / "harness"
            check_identity = freeze_harness(ROOT / "runner" / "harness", harness)
            identity = {"repo": fixture["repo"], "base": fixture["base"], "candidate": candidate,
                        "harness": check_identity, "image": image, "environment": "no-network/readonly/1cpu/512m"}
            fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
            evidence.update(identity=identity, fingerprint=fingerprint)
            results = []
            for label, source, test in [("Original behavior", base_dir, "check.py::test_coupon_applies_once"),
                                        ("Candidate behavior", candidate_dir, "check.py::test_coupon_applies_once"),
                                        ("Adjacent behavior", candidate_dir, "check.py::test_adjacent_zero_coupon check.py::test_adjacent_empty_cart")]:
                job.update(stage=label)
                # Test selectors are a fixed allowlist, never arbitrary chat or browser input.
                result = runner.run_check(source, harness, test, image)
                results.append(result)
                evidence["stages"].append({"name": label, "outcome": result.outcome, "assertion": result.assertion,
                    "collected": result.collected, "output": result.output})
            outcome = classify(*results, "test_coupon_applies_once")
        except Exception as exc:
            evidence["error"] = str(exc)[:500]
        finally:
            evidence["elapsed_ms"] = round((time.monotonic() - started) * 1000)
            store.save_run(case_id, run_id, fingerprint or run_id, outcome, evidence)
            job.update(running=False, stage="Complete", outcome=outcome)

    @app.post("/api/cases/{case_id}/run", dependencies=[Depends(authorize)], status_code=202)
    def run(case_id: str, payload: RunRequest, background: BackgroundTasks):
        with lock:
            try:
                case = store.get_case(case_id)
            except KeyError as exc:
                raise HTTPException(404, "Case not found") from exc
            if job.get("running"):
                raise HTTPException(409, "A verification is already running.")
            if not runner_status()["ready"]:
                raise HTTPException(503, runner_status()["message"])
            try:
                image = runner.image_identity()
            except RunnerUnavailable as exc:
                raise HTTPException(503, str(exc)) from exc
            manifest = data_dir / "demo.json"
            if not manifest.exists():
                raise HTTPException(409, "Prepare the controlled fixture first.")
            fixture = json.loads(manifest.read_text())
            candidate = fixture["candidates"][payload.candidate]
            if case["revision"] != payload.revision:
                raise HTTPException(409, "Case changed. Reload before running.")
            if case["candidate"] != candidate:
                store.set_candidate(case_id, candidate, case["revision"])
            run_id = uuid4().hex
            job.clear()
            job.update(running=True, id=run_id, case_id=case_id, stage="Starting isolated worker")
            background.add_task(execute, case_id, run_id, candidate, fixture, image)
            return {"execution_id": run_id}

    if (ROOT / "web" / "dist").exists():
        app.mount("/", StaticFiles(directory=ROOT / "web" / "dist", html=True), name="web")
    return app


app = create_app()
