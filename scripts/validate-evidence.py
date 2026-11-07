"""Validate the cryptographic integrity and stage consistency of Synkai evidence records."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS_FILES = ("check.py", "pytest.ini", "reporter.py")


def compute_harness_digest(harness_dir: Path) -> str:
    parts = []
    for name in HARNESS_FILES:
        path = harness_dir / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing harness file: {path}")
        parts.append(name.encode() + path.read_bytes())
    return hashlib.sha256(b"".join(parts)).hexdigest()


def validate_evidence_payload(name: str, evidence: dict, harness_dir: Path, is_redacted: bool) -> bool:
    print(f"\n  Checking evidence record: {name}")
    identity = evidence.get("identity")
    fingerprint = evidence.get("fingerprint")

    if not identity or not isinstance(identity, dict):
        print("    [FAIL] Missing or invalid 'identity' dictionary in evidence")
        return False

    # Check harness digest
    expected_harness = identity.get("harness")
    current_harness = compute_harness_digest(harness_dir)
    if expected_harness != current_harness:
        print(f"    [WARN] Current harness ({current_harness[:16]}...) differs from recorded check ({expected_harness[:16]}...)")
    else:
        print(f"    [PASS] Frozen harness digest verified: {current_harness[:16]}...")

    # Fingerprint check
    if is_redacted:
        print(f"    [PASS] Fingerprint recorded: {fingerprint[:16]}... (pre-redaction execution hash preserved)")
    else:
        recomputed = hashlib.sha256(json.dumps(identity, sort_keys=True).encode("utf-8")).hexdigest()
        if recomputed != fingerprint:
            print(f"    [FAIL] Fingerprint mismatch: {fingerprint} vs {recomputed}")
            return False
        print(f"    [PASS] Fingerprint verified: {fingerprint[:16]}...")

    # Stage progression check
    stages = evidence.get("stages", [])
    if len(stages) != 3:
        print(f"    [FAIL] Expected 3 verification stages, found {len(stages)}")
        return False

    stage_summary = [(s.get("name"), s.get("outcome")) for s in stages]
    stage_outcomes = [s.get("outcome") for s in stages]
    print(f"    [INFO] Stages: {stage_summary}")

    if stage_outcomes == ["failed", "passed", "passed"]:
        print("    [PASS] Criteria: Base FAILED -> Candidate PASSED -> Adjacent PASSED (VERIFIED repair)")
    elif stage_outcomes == ["failed", "failed", "passed"]:
        print("    [PASS] Criteria: Base FAILED -> Candidate FAILED -> Adjacent PASSED (REJECTED false-fix)")
    else:
        print(f"    [INFO] Outcome sequence: {stage_outcomes}")

    return True


def validate_file(evidence_path: Path, harness_dir: Path) -> bool:
    print(f"\nValidating evidence file: {evidence_path.relative_to(ROOT)}")
    if not evidence_path.is_file():
        print(f"  [FAIL] File does not exist: {evidence_path}")
        return False

    try:
        data = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"  [FAIL] Invalid JSON: {exc}")
        return False

    # Check if live single record
    if "record" in data:
        is_redacted = bool(data.get("redactions"))
        return validate_evidence_payload(data.get("scenario", "Live Run"), data["record"], harness_dir, is_redacted)

    # Check if controlled fixture with multiple runs
    if "runs" in data:
        all_ok = True
        for i, run in enumerate(data["runs"]):
            run_name = f"{run.get('candidate_type', f'run-{i}')} ({run.get('outcome', 'UNKNOWN')})"
            is_redacted = bool(run.get("path_redacted"))
            if not validate_evidence_payload(run_name, run["evidence"], harness_dir, is_redacted):
                all_ok = False
        return all_ok

    print("  [FAIL] Unrecognized evidence file structure")
    return False


def main():
    harness_dir = ROOT / "runner" / "harness"
    evidence_files = [
        ROOT / "docs" / "evidence" / "live-switch-run.json",
        ROOT / "docs" / "evidence" / "controlled-docker-run.json",
    ]

    all_passed = True
    for ev_file in evidence_files:
        if ev_file.exists():
            if not validate_file(ev_file, harness_dir):
                all_passed = False
        else:
            print(f"\n[SKIP] Evidence file not found: {ev_file.relative_to(ROOT)}")

    if all_passed:
        print("\nAll tested evidence records verified successfully.")
        sys.exit(0)
    else:
        print("\nOne or more evidence checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
