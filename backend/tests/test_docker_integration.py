"""Opt-in real-container checks: SYNKAI_DOCKER_TESTS=1 python -m pytest -m integration."""
import os

import pytest
from fastapi.testclient import TestClient

from synkai.api import create_app


@pytest.mark.integration
@pytest.mark.skipif(os.environ.get("SYNKAI_DOCKER_TESTS") != "1", reason="Requires an explicitly enabled Docker engine and built worker image")
def test_real_worker_rejects_false_fix_and_verifies_repair(tmp_path):
    with TestClient(create_app(data_dir=tmp_path), base_url="http://localhost") as client:
        assert client.get("/api/state").json()["runner"]["ready"]
        headers = {"Origin": "http://localhost:8787"}
        response = client.post("/api/demo", headers=headers)
        assert response.status_code == 200, response.text
        case_id = response.json()["id"]
        for candidate, expected in (("false-fix", "REJECTED"), ("real-fix", "VERIFIED")):
            case = client.get("/api/state").json()["cases"][0]
            response = client.post(f"/api/cases/{case_id}/run", headers=headers,
                                   json={"candidate": candidate, "revision": case["revision"]})
            assert response.status_code == 202, response.text
            case = client.get("/api/state").json()["cases"][0]
            assert case["current_outcome"] == expected, case["runs"][-1]
            evidence = case["runs"][-1]["evidence"]
            assert len(evidence["stages"]) == 3
            assert evidence["stages"][0]["assertion"] == "test_coupon_applies_once"
            assert evidence["stages"][2]["outcome"] == "passed"
            assert evidence["identity"]["image"].startswith("sha256:")
            assert evidence["model_calls"] == 0
        assert len(case["runs"]) == 2
