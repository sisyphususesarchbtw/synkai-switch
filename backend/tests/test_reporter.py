import json
import os
from pathlib import Path
import subprocess
import sys

HARNESS = Path(__file__).resolve().parents[2] / "runner" / "harness"


def report_for(tmp_path, body):
    (tmp_path / "test_contract.py").write_text("def test_coupon_applies_once():\n    " + body + "\n")
    env = dict(os.environ, PYTHONPATH=str(HARNESS), PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run([sys.executable, "-m", "pytest", "-p", "reporter", "-p", "no:cacheprovider", "-q", "test_contract.py"],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=20)
    return json.loads(next(line.removeprefix("SYNKAI_REPORT:") for line in result.stdout.splitlines() if line.startswith("SYNKAI_REPORT:")))


def test_runtime_error_cannot_masquerade_as_expected_assertion(tmp_path):
    report = report_for(tmp_path, "raise ValueError('dependency failed')")
    assert report["errors"] == 1
    assert report["assertion"] is None


def test_actual_check_assertion_retains_its_identity(tmp_path):
    report = report_for(tmp_path, "assert 8100 == 9000")
    assert report["errors"] == 0
    assert report["assertion"] == "test_coupon_applies_once"
