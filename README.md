# Synkai

An evidence workspace for checking whether a proposed code change fixes the agreed behavior.

The first case is a checkout bug: a 10% coupon is applied twice. One candidate changes its own test to accept the wrong total. Another repairs the implementation. Synkai runs the same independent check against the original revision and the candidate, then checks adjacent behavior.

## Current build

- React workspace with candidate selection, immutable execution history and raw evidence.
- FastAPI service and SQLite case storage; session-protected local actions.
- Controlled fixture containing real Git commits, created on demand.
- Docker worker with read-only source/check mounts, no network, CPU/memory/time limits.
- Evidence bound to the candidate, original revision, check digest and container image. Changed inputs expire previous evidence; contradictory replays remain inconclusive.

**Status:** the service, UI and real Docker verification run locally. The test-only candidate was rejected; the behavioral repair was verified using the unchanged check. Live Switch handoffs and coding-agent integration are the next milestone; they are not implemented or simulated in this build. This is a verification foundation, not yet a complete hackathon entry.

## Run locally

Requires Python 3.12+, Node 22.18+, Git, and Docker Desktop with Linux containers. Docker is needed for verification, but the workspace can start without it.

Windows PowerShell, from the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
npm.cmd --prefix web ci
npm.cmd --prefix web run build
.\scripts\start.ps1
```

Open [the local workspace](http://127.0.0.1:8787/). Prepare the case to create its local Git history. Then start Docker Desktop and build the worker:

```powershell
.\scripts\build-runner.ps1
```

Verify the **Test-only change**, then the **Behavioral repair**. Observed outcomes on November 6, 2026 were **REJECTED** (8.070 seconds) and **VERIFIED** (8.122 seconds), including all three isolated stages per candidate. These are single local measurements, not performance benchmarks. [Inspect the recorded evidence](docs/evidence/controlled-docker-run.json). An unavailable engine disables execution and leaves existing records readable.

On Windows, enabling Virtual Machine Platform may require a full Windows restart before Docker works. Restarting Docker alone is insufficient. See [Docker's WSL setup](https://docs.docker.com/desktop/features/wsl/).

## Checks

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm.cmd --prefix web test
npm.cmd --prefix web run build
```

Tests cover false fixes, placebo checks, runtime errors, stale inputs, conflicting replays, persistence, local API protections, frozen harness snapshots and candidate-specific UI status. They do not substitute for a real container or Switch run. GitHub Actions runs the backend tests and interface checks on pushes and pull requests.

With Docker running and the worker image built, enable the real-container integration test:

```powershell
$env:SYNKAI_DOCKER_TESTS = '1'
.\.venv\Scripts\python.exe -m pytest -q
```

The full backend suite passed 24 tests with that option enabled. The integration test creates its own Git fixture and exercises both candidates through the API and real worker. It is skipped in ordinary runs without the environment variable.

## Layout

| Path | Purpose |
| --- | --- |
| `backend/src/synkai` | Local API, evidence rules, storage and Docker execution |
| `backend/tests` | Behavior and regression tests |
| `runner` | Container definition and verifier-owned check/reporting harness |
| `web` | React/TypeScript workspace |
| `scripts` | Local startup and runner build |
| `assets/brand` | Original artwork and approved paired-bracket mark |

Local fixture repositories, execution snapshots and SQLite state are stored in ignored `.local/`. Credentials and generated dependencies are excluded from Git. The current worker supports only this controlled Python fixture; it is not a general service for hostile code. A verified result applies to its recorded checks and inputs, not general program correctness.

Built by Stillpoint for [Flip the Switch](https://www.wemakedevs.org/hackathons/switch).
