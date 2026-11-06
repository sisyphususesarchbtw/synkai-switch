# Setup and recovery

Use the [root README](../README.md) for Windows setup. Requires one trusted operator, Git, Python 3.12+, Node 22.18+, Docker Linux containers and an authenticated Codex CLI. The real live run used Windows/WSL 2, Docker Engine 29.9.2, Codex CLI 0.160.0, Python 3.14 and Node 24.19. CI uses Python 3.12 and Node 22.

Ports are 8787 (Synkai), 8790 (gateway), 8791 (Switch API), 8792 (Mattermost), 8793 (Postgres), all loopback. Stop if another service owns these ports. The `synkai-switch` Compose project retains its volumes; setup does not delete them.

## Linux / macOS

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install -e . --no-deps
npm --prefix web ci
npm --prefix web run build
.venv/bin/python -m synkai.setup prepare
docker compose -p synkai-switch --env-file .local/switch/.env -f .local/switch/compose.yaml --profile collab --profile gateway up -d
docker compose -p synkai-switch --env-file .local/switch/.env -f .local/switch/compose.yaml --profile collab --profile gateway wait setup
docker build -t synkai-runner:local runner
docker build -t synkai-coder:local coding-worker
# Review the credential scope in README before selecting your existing login.
.venv/bin/python -m synkai.setup connect --auth-file "$HOME/.codex/auth.json"
.venv/bin/python -m synkai --config .local/switch/runtime-config.json
```

In a second terminal: `.venv/bin/python -m uvicorn synkai.api:app --host 127.0.0.1 --port 8787`. These portability commands are provided; the real live run was on Windows. This is a local single-operator prototype, not public multi-user hosting.

## Retained setup

`prepare` generates secrets once, verifies the official Compose file and creates the authored fixture's Git history. `connect` registers owned agents once, derives the operator from the linked Mattermost identity and creates a room. It retains existing runtime configuration. Inspect existing private files instead of overwriting credentials.

Official Compose commit: `6ab2ff463ad9518920ba2a15b182b1d2e760fd9f`; normalized LF SHA-256: `cba238878078cf3d77fd9e136ef432f1ce5fd1bfe597acd172b9faa6720f0121`. Images are tagged server 0.31.0; verification binds the actual image digest. The coder image pins Codex CLI 0.160.0. The unchanged Switch stack has its own [upstream license](https://github.com/sandbox-quantum/switch/blob/6ab2ff463ad9518920ba2a15b182b1d2e760fd9f/LICENSE).

## Recovery

- **Docker unavailable:** start Docker Desktop. WSL 2/Virtual Machine Platform changes can require a full Windows restart. Records remain readable.
- **Switch setup pending:** inspect `docker compose -p synkai-switch --env-file .local/switch/.env -f .local/switch/compose.yaml --profile collab --profile gateway logs setup`. Wait for identity linking before `connect`.
- **Disconnected:** restore the stack; connections reuse IDs and cursors. Explicit gap/refused/evicted events stop for inspection.
- **Coding stopped:** inspect the private candidate JSONL log. It consumes its reserved attempt. Exact operator `retry coupon-01` is available after an inconclusive first attempt. No third call runs automatically.
- **Supervisor interrupted:** work interrupted during coding/verification becomes inconclusive on restart. Cleanup targets only container names associated with its own job logs. Budgets remain unchanged. Inspect before retrying; never edit SQLite to force a pass or extra attempt.
- **Inputs changed:** old evidence remains historical and cannot justify acceptance. Restore recorded inputs or conduct a fresh approved evaluation.

This version handles one active authored case. A separate demonstration needs separate local state and room configuration; do not silently reset the record or run two supervisors on the same agent connection.

## Fresh checkout

Clone, install committed dependencies, run backend tests and UI build, then `synkai.setup prepare` and Compose `config --quiet`. This proves setup does not depend on the developer's ignored vendor checkout. A full first deployment still requires registry access, Docker and the operator's provider login. The recorded live run and real-container integration supply separate operational evidence.
