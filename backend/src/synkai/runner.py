"""Run only the repository's controlled fixture in a restricted Docker job."""
import json
import hashlib
import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

from .verification import CheckResult


class RunnerUnavailable(RuntimeError):
    pass


HARNESS_FILES = ("check.py", "pytest.ini", "reporter.py")


def harness_digest(harness: Path) -> str:
    return hashlib.sha256(b"".join(name.encode() + (harness / name).read_bytes()
                                  for name in HARNESS_FILES)).hexdigest()


def freeze_harness(source: Path, destination: Path) -> str:
    destination.mkdir(parents=True, exist_ok=False)
    for name in HARNESS_FILES:
        shutil.copyfile(source / name, destination / name)
    return harness_digest(destination)


def docker_binary() -> str:
    installed = Path(r"C:\Program Files\Docker\Docker\resources\bin\docker.exe")
    return shutil.which("docker") or (str(installed) if installed.exists() else "docker")


def container_command(binary: str, image: str, source: Path, harness: Path,
                      test: str, name: str) -> list[str]:
    return [binary, "run", "--rm", "--name", name, "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--user", "65534:65534",
            "--cpus", "1", "--memory", "512m", "--pids-limit", "64",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=32m", "-v", f"{source.resolve()}:/subject:ro",
            "-v", f"{harness.resolve()}:/harness:ro", "-e", "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
            "-e", "PYTHONDONTWRITEBYTECODE=1", "--workdir", "/harness", image,
            "python", "-m", "pytest", "-c", "/harness/pytest.ini", "-p", "reporter", "-p", "no:cacheprovider", "-q", *test.split()]


class DockerRunner:
    def __init__(self, binary: str | None = None):
        self.binary = binary or docker_binary()

    def status(self) -> dict:
        try:
            result = subprocess.run([self.binary, "info", "--format", "{{.ServerVersion}}"],
                                    capture_output=True, text=True, timeout=4)
            if result.returncode == 0:
                return {"ready": True, "version": result.stdout.strip(), "message": "Docker engine is available"}
        except (OSError, subprocess.TimeoutExpired):
            pass
        return {"ready": False, "message": "Docker engine is unavailable. Start Docker Desktop; Windows may require Virtual Machine Platform and a restart."}

    def image_identity(self) -> str:
        try:
            result = subprocess.run([self.binary, "image", "inspect", "synkai-runner:local", "--format", "{{.Id}}"],
                                    capture_output=True, text=True, timeout=5, check=True)
            identity = result.stdout.strip()
            if not identity.startswith("sha256:"):
                raise RunnerUnavailable("Runner image identity is invalid")
            return identity
        except (OSError, subprocess.SubprocessError) as exc:
            raise RunnerUnavailable("Build the runner image first: docker build -t synkai-runner:local runner") from exc

    def run_check(self, source: Path, harness: Path, test: str, image: str) -> CheckResult:
        if not self.status()["ready"]:
            raise RunnerUnavailable(self.status()["message"])
        name = "synkai-" + uuid4().hex
        argv = container_command(self.binary, image, source, harness, test, name)
        # Logs go to a bounded file instead of an unbounded capture buffer.
        import tempfile
        import time
        with tempfile.TemporaryFile() as output:
            process = subprocess.Popen(argv, stdout=output, stderr=subprocess.STDOUT)
            started = time.monotonic()
            failure = None
            try:
                while process.poll() is None:
                    if time.monotonic() - started > 60:
                        failure = "timeout"
                        break
                    if output.tell() > 65536:
                        failure = "output_limit"
                        break
                    time.sleep(0.05)
                if failure:
                    process.kill()
                    process.wait(timeout=5)
                output.seek(0)
                raw = output.read(65537)
                text = raw[:65536].decode("utf-8", errors="replace")
                if failure or len(raw) > 65536:
                    return CheckResult("timeout" if failure == "timeout" else "error", collected=0, output=text + "\n[execution interrupted or output truncated]")
                return parse_report(text, process.returncode)
            finally:
                if process.poll() is None:
                    process.kill()
                try:
                    subprocess.run([self.binary, "rm", "-f", name], capture_output=True, timeout=5)
                except (OSError, subprocess.TimeoutExpired):
                    pass


def parse_report(output: str, exit_code: int) -> CheckResult:
    try:
        reports = [line[len("SYNKAI_REPORT:"):] for line in output.splitlines() if line.startswith("SYNKAI_REPORT:")]
        if len(reports) != 1:
            raise ValueError("Missing or ambiguous report")
        data = json.loads(reports[0])
        outcome = data["outcome"]
        expected_exit = 0 if outcome == "passed" else 1
        if exit_code != expected_exit or outcome not in {"passed", "failed"} or data.get("skipped", 0) or data.get("errors", 0):
            raise ValueError("Incomplete execution")
        return CheckResult(outcome, data.get("assertion"), int(data["collected"]), output)
    except (ValueError, KeyError, TypeError):
        return CheckResult("error", collected=0, output=output)
