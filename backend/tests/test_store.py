import pytest
from synkai.store import Store, Conflict


def test_candidate_change_expires_previous_evidence(tmp_path):
    store = Store(tmp_path / "cases.sqlite")
    case = store.create_case("Coupon must apply once", "base-1")
    store.set_candidate(case["id"], "candidate-1", expected_revision=0)
    store.save_run(case["id"], "run-1", "fingerprint-1", "VERIFIED", {"candidate": "candidate-1"})
    assert store.get_case(case["id"])["current_outcome"] == "VERIFIED"
    store.set_candidate(case["id"], "candidate-2", expected_revision=1)
    assert store.get_case(case["id"])["current_outcome"] == "STALE"
    assert len(store.get_case(case["id"])["runs"]) == 1


def test_duplicate_execution_is_stored_once_but_explicit_replay_is_distinct(tmp_path):
    store = Store(tmp_path / "cases.sqlite")
    case = store.create_case("Behavior", "base")
    store.save_run(case["id"], "run-1", "same-inputs", "VERIFIED", {})
    store.save_run(case["id"], "run-1", "same-inputs", "VERIFIED", {})
    store.save_run(case["id"], "run-2", "same-inputs", "REJECTED", {})
    store.save_run(case["id"], "run-3", "same-inputs", "VERIFIED", {})
    detail = store.get_case(case["id"])
    assert len(detail["runs"]) == 3
    assert detail["current_outcome"] == "INCONCLUSIVE"
    assert detail["inconsistent"] is True


def test_stale_revision_cannot_overwrite_candidate(tmp_path):
    store = Store(tmp_path / "cases.sqlite")
    case = store.create_case("Behavior", "base")
    store.set_candidate(case["id"], "first", expected_revision=0)
    with pytest.raises(Conflict):
        store.set_candidate(case["id"], "second", expected_revision=0)
    assert store.get_case(case["id"])["candidate"] == "first"


def test_case_and_evidence_survive_restart(tmp_path):
    path = tmp_path / "cases.sqlite"
    first = Store(path)
    case = first.create_case("Behavior", "base")
    first.save_run(case["id"], "run-1", "inputs", "REJECTED", {"actual": 8100})
    restored = Store(path).get_case(case["id"])
    assert restored["runs"][0]["evidence"]["actual"] == 8100


def test_changed_harness_or_image_expires_current_evidence(tmp_path):
    store = Store(tmp_path / "cases.sqlite")
    case = store.create_case("Behavior", "base")
    store.save_run(case["id"], "run", "inputs", "VERIFIED", {"identity": {"harness": "old-check", "image": "old-image"}})
    assert store.get_case(case["id"], current_inputs={"harness": "new-check", "image": "old-image"})["current_outcome"] == "STALE"
    assert store.get_case(case["id"], current_inputs={"harness": "old-check", "image": "new-image"})["current_outcome"] == "STALE"
