"""Validate the integrity and stage consistency of Synkai evidence records.

Fails closed on any invalid, tampered, or missing record.
Explicitly distinguishes verifiable integrity from checks that cannot be performed on redacted artifacts.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS_FILES = ("check.py", "pytest.ini", "reporter.py")
HEX_SHA_REGEX = re.compile(r"^[a-f0-9]{40,64}$")


def compute_harness_digest(harness_dir: Path) -> str:
    """Compute the SHA-256 digest of the frozen harness files."""
    parts = []
    for name in HARNESS_FILES:
        path = harness_dir / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing harness file: {path}")
        parts.append(name.encode() + path.read_bytes())
    return hashlib.sha256(b"".join(parts)).hexdigest()


def validate_evidence_payload(name: str, evidence: dict, harness_dir: Path, is_redacted: bool) -> tuple[bool, str]:
    """Validate a single evidence dictionary. Returns (success: bool, reason: str)."""
    identity = evidence.get("identity")
    fingerprint = evidence.get("fingerprint")

    if not isinstance(identity, dict):
        return False, f"Missing or non-dict 'identity' in record: {name}"

    if not fingerprint or not isinstance(fingerprint, str) or not HEX_SHA_REGEX.match(fingerprint):
        return False, f"Missing or malformed 'fingerprint' in record: {name}"

    # 1. Verify frozen harness digest (must match exactly)
    expected_harness = identity.get("harness")
    if not expected_harness or not isinstance(expected_harness, str):
        return False, f"Missing 'identity.harness' in record: {name}"

    try:
        current_harness = compute_harness_digest(harness_dir)
    except FileNotFoundError as exc:
        return False, str(exc)

    if expected_harness != current_harness:
        return False, (
            f"Harness mismatch in {name}!\n"
            f"        Recorded: {expected_harness}\n"
            f"        Computed: {current_harness}"
        )

    # 2. Check fingerprint
    if is_redacted:
        # Honest disclosure: Redacted public evidence substituted local paths.
        # The fingerprint cannot be recomputed from '<local-workspace>' strings.
        # We verify that commit hashes within identity are valid hex SHAs.
        base_sha = identity.get("base")
        cand_sha = identity.get("candidate")
        if not base_sha or not HEX_SHA_REGEX.match(base_sha):
            return False, f"Invalid base commit SHA in redacted record: {name}"
        if not cand_sha or not HEX_SHA_REGEX.match(cand_sha):
            return False, f"Invalid candidate commit SHA in redacted record: {name}"
        print(f"    [NOTE: REDACTED] {name}: Local path redacted for publication. Fingerprint ({fingerprint[:16]}...) was generated pre-redaction and cannot be recomputed from published text.")
    else:
        # Unredacted: must recompute and match exactly
        recomputed = hashlib.sha256(json.dumps(identity, sort_keys=True).encode("utf-8")).hexdigest()
        if recomputed != fingerprint:
            return False, (
                f"Fingerprint mismatch in {name}!\n"
                f"        Recorded: {fingerprint}\n"
                f"        Computed: {recomputed}"
            )
        print(f"    [PASS] Fingerprint verified: {fingerprint[:16]}...")

    # 3. Verify stage progression (must strictly match allowed criteria)
    stages = evidence.get("stages")
    if not isinstance(stages, list) or len(stages) != 3:
        return False, f"Expected exactly 3 verification stages in {name}, found {len(stages) if isinstance(stages, list) else 'none'}"

    stage_outcomes = [s.get("outcome") for s in stages if isinstance(s, dict)]
    expected_names = ["Original behavior", "Candidate behavior", "Adjacent behavior"]
    actual_names = [s.get("name") for s in stages if isinstance(s, dict)]

    if actual_names != expected_names:
        return False, f"Stage name sequence mismatch in {name}: {actual_names} != {expected_names}"

    # Strict stage validation:
    # VERIFIED repair: Base must FAIL, Candidate must PASS, Adjacent must PASS
    # REJECTED false-fix: Base must FAIL, Candidate must FAIL, Adjacent must PASS
    if stage_outcomes == ["failed", "passed", "passed"]:
        print(f"    [PASS] Stages valid: Base FAILED -> Candidate PASSED -> Adjacent PASSED (VERIFIED repair)")
    elif stage_outcomes == ["failed", "failed", "passed"]:
        print(f"    [PASS] Stages valid: Base FAILED -> Candidate FAILED -> Adjacent PASSED (REJECTED false-fix)")
    else:
        return False, f"Invalid or unexpected stage progression in {name}: {stage_outcomes}"

    return True, "OK"


def validate_file(evidence_path: Path, harness_dir: Path) -> bool:
    """Validate an evidence file. Fails closed on any error."""
    print(f"\nValidating evidence file: {evidence_path.name}")
    if not evidence_path.is_file():
        print(f"  [FAIL] Missing required evidence file: {evidence_path}")
        return False

    try:
        data = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  [FAIL] Unable to parse JSON file {evidence_path}: {exc}")
        return False

    if "record" in data:
        is_redacted = bool(data.get("redactions"))
        scenario = data.get("scenario", "Live Run")
        ok, reason = validate_evidence_payload(scenario, data["record"], harness_dir, is_redacted)
        if not ok:
            print(f"  [FAIL] {reason}")
            return False
        return True

    if "runs" in data:
        all_ok = True
        for i, run in enumerate(data["runs"]):
            run_name = f"{run.get('candidate_type', f'run-{i}')} ({run.get('outcome', 'UNKNOWN')})"
            is_redacted = bool(run.get("path_redacted"))
            ok, reason = validate_evidence_payload(run_name, run.get("evidence", {}), harness_dir, is_redacted)
            if not ok:
                print(f"  [FAIL] {reason}")
                all_ok = False
        return all_ok

    print(f"  [FAIL] Unrecognized evidence schema in {evidence_path}")
    return False


def run_all(evidence_files: list[Path], harness_dir: Path) -> bool:
    """Validate all required evidence files. Fails closed if any file fails or is missing."""
    if not evidence_files:
        print("[FAIL] No evidence files specified for validation.")
        return False

    all_passed = True
    for ev_file in evidence_files:
        if not validate_file(ev_file, harness_dir):
            all_passed = False

    return all_passed


def main():
    harness_dir = ROOT / "runner" / "harness"
    evidence_files = [
        ROOT / "docs" / "evidence" / "live-switch-run.json",
        ROOT / "docs" / "evidence" / "controlled-docker-run.json",
    ]

    passed = run_all(evidence_files, harness_dir)
    if passed:
        print("\nAll required evidence records verified successfully.")
        sys.exit(0)
    else:
        print("\nOne or more evidence verification checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
