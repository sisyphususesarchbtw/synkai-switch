"""Prepare a controlled, local Git history. Never runs candidate Python on host."""
import hashlib
import json
import subprocess
from pathlib import Path

BASE = "def total_after_coupon(cents, percent):\n    discounted = cents * (100 - percent) // 100\n    return discounted * (100 - percent) // 100\n"
FIXED = "def total_after_coupon(cents, percent):\n    return cents * (100 - percent) // 100\n"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, timeout=15).stdout.strip()


def prepare_demo(data_dir: Path) -> dict:
    manifest = data_dir / "demo.json"
    if manifest.exists():
        return json.loads(manifest.read_text())
    repo = data_dir / "fixture-repository"
    if repo.exists():
        raise ValueError("An incomplete fixture repository exists. Inspect it before creating another.")
    repo.mkdir(parents=True)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Synkai controlled fixture")
    git(repo, "config", "user.email", "fixture@example.invalid")
    (repo / "cart.py").write_text(BASE)
    (repo / "test_cart.py").write_text("from cart import total_after_coupon\ndef test_coupon():\n    assert total_after_coupon(10000, 10) == 9000\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture: reproduce duplicated coupon application")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "test_cart.py").write_text("from cart import total_after_coupon\ndef test_coupon():\n    assert total_after_coupon(10000, 10) == 8100\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture: false fix weakens expected behavior")
    false = git(repo, "rev-parse", "HEAD")
    (repo / "cart.py").write_text(FIXED)
    (repo / "test_cart.py").write_text("from cart import total_after_coupon\ndef test_coupon():\n    assert total_after_coupon(10000, 10) == 9000\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture: apply the coupon exactly once")
    fixed = git(repo, "rev-parse", "HEAD")
    result = {"repo": str(repo.resolve()), "base": base, "candidates": {"false-fix": false, "real-fix": fixed}}
    manifest.write_text(json.dumps(result, indent=2))
    return result


def export_snapshot(repo: Path, revision: str, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("cart.py", "test_cart.py"):
        (destination / name).write_text(git(repo, "show", f"{revision}:{name}") + "\n")
