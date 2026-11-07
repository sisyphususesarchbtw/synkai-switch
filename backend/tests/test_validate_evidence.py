"""Negative and positive unit tests for scripts/validate-evidence.py.

Verifies fail-closed behavior for tampered digests, fingerprints, stage progressions,
corrupted JSON, and missing evidence files.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

# Ensure scripts directory is importable
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import importlib.util
spec = importlib.util.spec_from_file_location("validate_evidence", ROOT / "scripts" / "validate-evidence.py")
val_ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(val_ev)


@pytest.fixture
def harness_dir():
    return ROOT / "runner" / "harness"


@pytest.fixture
def sample_valid_evidence():
    harness_hash = val_ev.compute_harness_digest(ROOT / "runner" / "harness")
    identity = {
        "base": "e96334c8262eabdf6fde5c0c47a7d8bcff22a3cd",
        "candidate": "87ea36f955dd8d32843a30f9edddce3ea77179ff",
        "harness": harness_hash,
        "image": "sha256:2c687e3d83f9910c7e5f777135a7ad86a249cec4e2aa4ab60a4b30b2b40e64e5",
        "environment": "no-network/readonly/1cpu/512m",
        "repo": "/workspace/repo",
    }
    fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "identity": identity,
        "fingerprint": fingerprint,
        "stages": [
            {"name": "Original behavior", "outcome": "failed"},
            {"name": "Candidate behavior", "outcome": "passed"},
            {"name": "Adjacent behavior", "outcome": "passed"},
        ],
    }


def test_valid_evidence_passes(sample_valid_evidence, harness_dir):
    ok, reason = val_ev.validate_evidence_payload("test-run", sample_valid_evidence, harness_dir, is_redacted=False)
    assert ok is True
    assert reason == "OK"


def test_tampered_harness_fails(sample_valid_evidence, harness_dir):
    tampered = copy.deepcopy(sample_valid_evidence)
    tampered["identity"]["harness"] = "0000000000000000000000000000000000000000000000000000000000000000"
    ok, reason = val_ev.validate_evidence_payload("tampered-harness", tampered, harness_dir, is_redacted=False)
    assert ok is False
    assert "Harness mismatch" in reason


def test_tampered_fingerprint_unredacted_fails(sample_valid_evidence, harness_dir):
    tampered = copy.deepcopy(sample_valid_evidence)
    tampered["fingerprint"] = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    ok, reason = val_ev.validate_evidence_payload("tampered-fingerprint", tampered, harness_dir, is_redacted=False)
    assert ok is False
    assert "Fingerprint mismatch" in reason


def test_unexpected_stage_progression_fails(sample_valid_evidence, harness_dir):
    tampered = copy.deepcopy(sample_valid_evidence)
    # Both base and candidate passed (placebo check)
    tampered["stages"][0]["outcome"] = "passed"
    ok, reason = val_ev.validate_evidence_payload("placebo-check", tampered, harness_dir, is_redacted=False)
    assert ok is False
    assert "Invalid or unexpected stage progression" in reason


def test_missing_identity_fails(sample_valid_evidence, harness_dir):
    tampered = copy.deepcopy(sample_valid_evidence)
    del tampered["identity"]
    ok, reason = val_ev.validate_evidence_payload("no-identity", tampered, harness_dir, is_redacted=False)
    assert ok is False
    assert "Missing or non-dict 'identity'" in reason


def test_missing_evidence_file_fails(tmp_path, harness_dir):
    non_existent = tmp_path / "does_not_exist.json"
    assert val_ev.validate_file(non_existent, harness_dir) is False


def test_corrupted_json_fails(tmp_path, harness_dir):
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{ this is not valid json }", encoding="utf-8")
    assert val_ev.validate_file(corrupt, harness_dir) is False


def test_run_all_with_missing_files_fails(tmp_path, harness_dir):
    missing_list = [tmp_path / "missing1.json", tmp_path / "missing2.json"]
    assert val_ev.run_all(missing_list, harness_dir) is False


def test_actual_repo_evidence_files_pass(harness_dir):
    evidence_files = [
        ROOT / "docs" / "evidence" / "live-switch-run.json",
        ROOT / "docs" / "evidence" / "controlled-docker-run.json",
    ]
    assert val_ev.run_all(evidence_files, harness_dir) is True
