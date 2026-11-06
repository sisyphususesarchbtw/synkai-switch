# NYKT design specification

Date: November 6, 2026 IST. Status: proposed defaults finalized for implementation planning; product execution has not begun. Owner: solo participant, team Stillpoint.

## Why this exists

Reviewing a claimed agent fix requires agreement on behavior and evidence that the exact patch changes it. NYKT combines a real Switch discussion with a verifier-controlled executable check. The demonstration must show useful work and honest uncertainty, not staged messages presented as live execution.

## Approaches considered

1. Focused verification room: selected as the working direction after the user asked to proceed and finalize the project. Narrow deterministic defect supports a strong demo within the remaining event time.
2. General CI triage: useful pain evidence, but environmental diagnosis and historical flakiness would expand scope.
3. API release coordination: useful team workflow, but overlaps with mature diff/review products and needs realistic consumers.

Within the chosen direction, a local Python service with a browser UI is the proposed implementation. A CLI-only tool would weaken presentation; a new multiplayer IDE or distributed agent framework would exceed the solo scope. These technology choices are the assistant's defaults, not separately confirmed user preferences.

## Fixed boundaries

- Product NYKT; team Stillpoint; tagline Clarity, earned.; dark Zen interface per DESIGN.md.
- Primary track Business Workflow; also Code with Wispr and Best Blog; no core contribution.
- Python 3.12+ for the service; Node 22+ for frontend tooling; exact available versions checked before dependency installation.
- FastAPI + Pydantic + SQLite; React + TypeScript + Vite; Docker for verification jobs; pytest for the initial supported repository.
- One trusted local operator, one allowlisted repository and one active verification at a time. Backend and UI bind to loopback by default.
- Mattermost via Switch first. Discord after core acceptance only. No WhatsApp integration claim.
- Switch is the only collaboration/handoff path. Browser UI is a view plus authenticated commands to the room, not a parallel agent messaging system.
- Two agent identities, Fixer and Verifier. Use an existing Console-supported coding provider for Fixer; choose an actually authenticated installed provider in Task 1 and document it. No model name is assumed.
- The verifier service is a custom Switch agent plus a deterministic runner. It may use the same provider to draft a check, but the human approves the behavior and check before freezing it. Deterministic checks do not require model calls.
- No automatic public comments, merges, deployments or outbound messages outside the configured project room. A patch and evidence are enough for MVP; auto-opening a PR is stretch scope.

## Source of truth and trust

Switch is the conversation authority. SQLite is the case state/evidence index. The filesystem contains immutable check bundles and runtime artifacts. Separate agent prompts or same-user directories alone do not create an execution boundary. Fixer must run in a separate container/process account that can write only its candidate workspace and cannot reach the verifier store, checks, host filesystem, Docker control socket or verifier credentials. Give it only the credentials required for its own configured provider and room identity. If Console's selected provider cannot enforce that boundary, use a supported CLI in a restricted worker or a trusted separate runner host; record the actual boundary before claiming independence.

Before any repair, the operator chooses the allowlisted repository and full base SHA; persist both as trusted case input and freeze a source snapshot identity. Candidate.base_sha must equal that frozen SHA, and the returned candidate must be a commit in that same repository descended from that base. Reject unrelated history or substituted bases. Include repository identity, base SHA and their hashes in the evidence manifest and stale-input comparison. A corrected baseline is a new verification input that requires a new run.

Only the operator can approve expected behavior/checks. Validate the actual Switch sender identity against an operator allowlist; a quoted approval or an agent message cannot approve a check. Structured payloads are attached to addressed room messages; external text cannot become a shell command. Check bundles are reviewed executable content in the allowlisted local project, not arbitrary user uploads.

Docker jobs have no secrets, no Docker socket mount, no network, unprivileged user, read-only rootfs, read-only source/check mounts, bounded writable tmpfs, dropped capabilities and explicit resource/time/output limits. Dependencies are installed into a pinned runner image before jobs. This mitigates risk for trusted project fixtures; it is not a hardened hostile-code hosting platform. Fixer receives no runner control socket or verifier path.

## Case model and state

Case: id, room_id, source_message_id, reporter_id, report, expected_behavior, status, revision, created_at, updated_at.
Candidate: id, case_id, git_sha, base_sha, created_at. Use full commit SHA, never a mutable branch name as evidence identity.
CheckBundle: id, case_id, expected_behavior, files_sha256, harness_sha256, approved_by, approval_message_id, created_at.
Run: id, candidate_id, check_bundle_id, image_digest, env_digest, status, base_result, candidate_result, regression_result, artifact_manifest_sha256, elapsed_ms, created_at.
Decision: id, case_id, run_id, actor_id, outcome, source_message_id, created_at. Human acceptance and automated verification are distinct.

Case states: REPORTED -> NEEDS_INPUT -> CHECK_FROZEN -> REPRODUCING -> REPAIRING -> VERIFYING -> AWAITING_REVIEW -> CLOSED. An execution can end in VERIFIED, REJECTED or INCONCLUSIVE; evidence can subsequently be STALE. Run outcomes are not interchangeable with case lifecycle.

Every state mutation uses an expected integer revision; stale writes fail. Deduplicate Switch deliveries by (room_id, event_id); deduplicate run requests by a hash of case, candidate, check bundle, image and environment. Persist event receipt and transition in the same SQLite transaction. A queued dispatch is persisted in an outbox and retried with its stable id; delivery acknowledgement is not proof of verification. Establish native Switch send idempotency during setup. Regardless of native support, include a stable NYKT command_id in structured handoffs and transactionally deduplicate (room_id, receiver_agent_id, command_id) before acting. A transport retry can create another message/event id but must not create another repair attempt or consume the budget. Task 1 must confirm Fixer's receiver wrapper can enforce this before invoking its coding CLI.

## Verification semantics

Run the same frozen check and harness against exported base and candidate sources in clean containers. Do not execute pytest from the candidate checkout's config, conftest or plugins. Invoke the verifier-owned harness with explicit configuration and controlled import path. Fixtures initially contain a small pure Python module with no runtime dependencies.

The runner-owned plugin/report schema records collection, skips, errors, assertion identity and actual exit status. Expected reproduction requires the named behavioral assertion to fail; import errors, test-collection problems, timeouts and unknown failures are inconclusive. A missing report or a success exit with zero collected checks is inconclusive. The check must pass on candidate and adjacent checks must pass. Base/candidate use identical check bundle, harness, image and environment identities.

VERIFIED: expected base behavioral failure + candidate pass + required adjacent checks pass + all input identities match. REJECTED: reproducible candidate behavioral failure or confirmed adjacent regression. INCONCLUSIVE: neither result is justified, including check passes on base, skips, missing dependencies, interrupted execution or empty collection. A new candidate/check/environment invalidates the displayed current verification. This is empirical evidence, not formal proof.

Budget: 60 seconds per container run, 1 CPU, 512 MiB memory, 64 processes, 64 KiB stdout/stderr per stream with explicit truncation metadata. At most one initial attempt plus one repair candidate. Stop and ask the human if that fails. New verification requires an explicit action; no always-on retry loop.

## Collaboration

Use current Switch docs and pin the tested release. Current docs describe WebSocket events plus HTTP operations; SSE is deprecated. Discover operations at startup; do not invent a task protocol. New agent addressing defaults may exclude other agents, so explicitly configure the two identities to address one another within their owner's scope. Act only on events addressed to the agent. Preserve cursor/reconnect identity and answer pings.

Verifier asks the human to settle ambiguous behavior, freezes the check after a real authorized approval, and sends one targeted repair request to Fixer. Fixer returns a candidate SHA. Verifier posts the evidence summary and URL back through Switch. UI requests are translated to authenticated room actions; they cannot impersonate a Switch user by supplying a sender id. If a suitable user-authenticated operation is unavailable, keep approval exclusively in Mattermost and make the dashboard read-only for that action.

The first demo uses Mattermost. Discord credentials/setup are optional and never become a blocker for the core demo. Disconnects preserve readable evidence, label the room offline and prevent commands being silently accepted. Unaddressed messages must not cause agent chatter.

## API boundary

All routes local-only; session secret held server-side with an HttpOnly SameSite cookie for the UI; reject unknown Origin on mutations. Secrets never enter the frontend bundle.

- GET /health -> service, bridge state and worker availability.
- GET /api/cases -> CaseSummary[].
- GET /api/cases/{id} -> CaseDetail including evidence identity and source room URL.
- GET /api/cases/{id}/events -> server-sent UI updates (this is NYKT UI transport, not deprecated Switch agent SSE).
- POST /api/cases/{id}/actions -> {action, expected_revision, idempotency_key}; only allowlisted authenticated actions. Return 202 plus command id; room event confirms acceptance.
- GET /api/runs/{id}/evidence -> evidence JSON.
- GET /api/runs/{id}/artifacts/{artifact_id} -> manifest-resolved artifact only; no caller-provided filesystem paths.

## UI and demo

Implement /cases and /cases/:id as described in DESIGN.md. Show readable behavior first, then exact base/candidate/check/environment identities, result pair, next action, two agent states and original room link. Both revisions side by side. No invented speed or confidence score.

Controlled fixture: a date-window or pagination-boundary bug. Base is wrong; a false candidate weakens repository tests but leaves behavior wrong; a real candidate fixes the production module. Freeze verifier checks outside all three sources. Add cases for a check that passes on both versions and an unrelated runtime error. Label fixtures. Ideally add one small historical public fix with attribution if time remains.

## Scaling without premature infrastructure

Use project_id and case_id in durable records and artifact manifests; initially one allowlisted project. Keep SwitchBridge, CodingProvider, VerificationRunner and EvidenceStore as narrow interfaces. For multiple projects, add per-project queue/concurrency quotas, Postgres, object storage and isolated workers. Then design organization authentication and tenant separation. Do not claim this implementation handles untrusted multi-tenant repos or a benchmarked load.

## Validation and presentation

Acceptance cases: false fix rejected, real fix verified, unknown/setup failure inconclusive, stale revision invalidates, duplicate event causes no duplicate run, other agents cannot approve checks, verifier checks unaffected by candidate test/config modifications, and room disconnect never reports successful command delivery.

Measure real wall time, calls and model usage when available. Record unavailable costs as unknown. Test desktop 1440px and mobile 390px, keyboard focus, contrast, offline and inconclusive screens. Clean clone setup and a real Mattermost -> Switch -> Fixer -> Verifier -> human loop are required before claiming complete.

Blog and Wispr are parallel documentation work, not second products. Capture notes and actual Insights scorecard; publish only tested claims. Final submission fields still need checking in the registration/submission UI.

## Sources and limits

- https://useamoeba.com/faq — ownership, visible sessions, commit-pinned shared context, takeover. Inspiration only; not building an IDE.
- https://ryoku.dev/showroom — dark desktop reference. NYKT has its own tokens and layout.
- https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard — operator workspace reference.
- https://docs.switchagents.ai/switch-rooms/internals/agent-protocol — current transport and addressing.
- https://www.wemakedevs.org/hackathons/switch — tracks, deadline, Mattermost, side-entry evidence.

Open implementation prerequisite: Docker is not currently discoverable on PATH. Task 1 checks installation/runtime and Windows/WSL readiness. If a runnable isolated worker cannot be obtained promptly, provision one trusted Linux runner or reduce the demo claim; do not silently substitute unsafe local execution.
