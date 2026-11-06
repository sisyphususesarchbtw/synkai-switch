from pathlib import Path
import pytest
from synkai.runner import DockerRunner, RunnerUnavailable, container_command


def test_missing_runtime_stops_before_candidate_execution(tmp_path):
    runner = DockerRunner(binary=str(tmp_path / "missing-docker.exe"))
    with pytest.raises(RunnerUnavailable):
        runner.run_check(tmp_path, tmp_path, "test_coupon_applies_once", "missing-image")


def test_container_has_no_network_secrets_or_writable_source_mount():
    argv = container_command("docker", "sha256:test", Path("source"), Path("harness"), "check.py::test_coupon_applies_once", "synkai-test")
    assert argv[argv.index("--network") + 1] == "none"
    assert "--read-only" in argv
    assert argv[argv.index("--cap-drop") + 1] == "ALL"
    assert argv[argv.index("--user") + 1] == "65534:65534"
    assert all(":ro" in argv[i + 1] for i, arg in enumerate(argv) if arg == "-v")
    assert not any("docker.sock" in arg for arg in argv)


def test_adjacent_checks_are_separate_pytest_arguments():
    argv = container_command("docker", "sha256:test", Path("source"), Path("harness"), "check.py::test_a check.py::test_b", "synkai-test")
    assert argv[-2:] == ["check.py::test_a", "check.py::test_b"]


def test_frozen_harness_is_not_changed_by_working_tree_edits(tmp_path):
    from synkai.runner import freeze_harness, harness_digest
    source, frozen = tmp_path / "source", tmp_path / "frozen"
    source.mkdir()
    for name in ("check.py", "pytest.ini", "reporter.py"):
        (source / name).write_text("original")
    identity = freeze_harness(source, frozen)
    (source / "check.py").write_text("changed after original execution")
    assert harness_digest(frozen) == identity
    assert harness_digest(source) != identity
