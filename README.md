# Synkai

**Agent-written fixes, checked against an agreement they cannot rewrite.**

Synkai turns a bug report in a shared Switch room into an approved behavior, a real coding-agent patch, and independent before/after evidence. Built by **Stillpoint** for **Best Business Workflow** at [Flip the Switch](https://www.wemakedevs.org/hackathons/switch).

The demonstrated case is deliberately small: a 10% coupon on a 10000-cent cart is applied twice, leaving 8100 cents. The operator expects 9000. Fixer proposes a repair; Verifier runs the same frozen check on both revisions and checks zero-coupon and empty-cart behavior. The operator can inspect and accept the result in the original conversation.

## What actually works

- Two real Switch identities, **Fixer** and **Verifier**, collaborate with the operator in **Mattermost**. Targeted handoffs travel through Switch. Room instructions, a GitHub reference and a verifier-authored agreement document retain context.
- Fixer wraps authenticated **Codex CLI** in a restricted Docker container. It returns a structured source proposal; the supervisor applies only `cart.py` and creates a new Git commit. Verifier is a deterministic supervisor, not a second language model.
- The verifier runs original, candidate and adjacent checks in separate read-only, network-disabled Docker containers. Candidate tests cannot redefine the independent check.
- Durable message cursors, receipt-bound handoffs, exact operator identity checks, a two-attempt budget, and an OS-held supervisor lock protect the workflow.
- The monochrome React workspace shows the actual conversation, pending decision, patch, connection state, execution output and immutable evidence. Changed candidate, check or image identities expire current evidence.

**Observed November 6, 2026:** a live model-proposed repair was **VERIFIED** after the original failed the expected assertion, the candidate passed, and both adjacent checks passed. The successful coding attempt took **17.183 seconds**; independent verification took **13.111 seconds**. An earlier attempt stopped before changing files because nested shell isolation was unavailable. That failure and the explicitly delegated operator retry remain in the record. These are single local observations, not production benchmarks or claimed savings. Monetary model cost was not reported.

[Live evidence](docs/evidence/live-switch-run.json) · [Actual patch](docs/evidence/live-candidate.patch) · [Evaluation and limits](docs/evaluation.md) · [Build article](docs/building-synkai.md)

## Run the workspace

Requires Python 3.12+, Node 22.18+, Git, and Docker Desktop with Linux containers. On Windows, complete Docker's WSL 2 setup and any requested Windows restart first.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
npm.cmd --prefix web ci
npm.cmd --prefix web run build
.\scripts\start.ps1
```

Open [Synkai locally](http://127.0.0.1:8787/). Without live configuration it opens the labelled **controlled fixture**: compare an authored test-only false fix with an authored behavioral repair. Build the verifier image before executing either:

```powershell
.\scripts\build-runner.ps1
```

## Run the live Switch workflow

Sign in to the official Codex CLI first. The coding worker needs your existing `auth.json`. This explicit setup mounts that file **read-only** in the coding container: credentials are readable there for authentication, but cannot be modified through that mount. No Switch key, verifier harness, Docker socket or other home files are mounted. The CLI's sandbox remains enabled. This deployment is for your own local machine and account.

```powershell
# Replace with the existing Codex login file you choose to use.
.\scripts\setup-switch.ps1 -AuthFile "$env:USERPROFILE\.codex\auth.json"
```

The script downloads and verifies the official commit-pinned Switch Compose file, starts server **0.31.0** on loopback, builds both worker images, registers two owned identities and creates the Mattermost room. It generates private passwords once and retains them across restarts. First image pulls can take several minutes.

Start these in **two terminals**:

```powershell
.\scripts\start-live.ps1
```

```powershell
.\scripts\start.ps1
```

Sign in to [Mattermost](http://localhost:8792/) using private `.local/switch/login.txt`. Open **Synkai Evidence Room** and send:

```text
@synkai-verifier A 10% coupon is applied twice. On a 10000-cent cart I expect 9000 cents. Please investigate and ask me before freezing the check.
```

Read the proposal, then send `@synkai-verifier approve coupon-01`. Follow the conversation and [workspace](http://127.0.0.1:8787/). After reviewing a verified patch, send `@synkai-verifier accept coupon-01`. An explicitly approved retry is available only while an attempt remains. This release supports one active authored checkout case.

[Detailed setup and recovery](docs/setup.md) · [Switch channel and agent details](switch/README.md)

## Verify it

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm.cmd --prefix web test
npm.cmd --prefix web run build
# Include real Docker execution, with synkai-runner:local already built:
$env:SYNKAI_DOCKER_TESTS = '1'
.\.venv\Scripts\python.exe -m pytest -q
```

The November 6 verification run passed **61 backend tests**, including real Docker, **5 UI logic tests**, and the production build. A Starlette/httpx upstream deprecation warning remains visible. GitHub Actions checks the backend and interface. Automated tests do not substitute for the recorded live Switch run.

## Boundaries

This focused local prototype supports the supplied dependency-light Python checkout project. It does not support arbitrary repositories, Slack/Discord/WhatsApp deployment, production issue ingestion, automatic merging, or multi-user hosting. A pass covers the agreed checks and recorded inputs, not general program correctness. A Switch reference is context, not a repository credential grant.

Local state and credentials live in ignored `.local/`. Public evidence redacts filesystem prefixes and preserves original fingerprints with that limitation stated. The actual candidate's two-commit history is included as [a Git bundle](docs/evidence/live-candidate.bundle):

```powershell
git clone docs/evidence/live-candidate.bundle .local/inspect-candidate
git -C .local/inspect-candidate show 87ea36f955dd8d32843a30f9edddce3ea77179ff
```

The Switch stack is downloaded unchanged from [SandboxAQ's official repository](https://github.com/sandbox-quantum/switch/tree/6ab2ff463ad9518920ba2a15b182b1d2e760fd9f) under its own license. Synkai source uses this repository's [MIT license](LICENSE).
