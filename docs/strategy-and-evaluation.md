# Synkai strategy and evaluation
Research checked November 6, 2026 IST. Public project descriptions are author claims unless independently exercised. We have not run competitors or inspected all submissions.

## Decision
Primary: Best Business Workflow. Side: Code with Wispr. Secondary: Best Blog. Core Contribution remains conditional on assignment and main-build readiness.

Build one useful collaboration workflow: human-approved behavior becomes a frozen check that detects the original defect, passes on a repaired candidate and expires when verification inputs change. A general agent hub is the container, not the pitch.

## Hook, evidence, solution, metric
Hook: Your CI is green. Your bug is still there.
Evidence: show a candidate whose edited repository tests pass while the original defect still reproduces; expose the actual check and outputs.
Solution: human intent -> frozen check -> separate fixing agent -> independent before/after execution -> human review in the same Switch room.
Metric: false fixes accepted / tested false fixes; correct fixes verified / tested correct fixes; inconclusive cases / total cases; wall time and AI invocations per case.

USP: make the causal argument for a claimed fix inspectable by people and agents in one room. Red/green testing, commit-bound CI and stale-approval invalidation already exist. Distinction rests on the focused workflow, execution and presentation, not an exclusive algorithm.

## Public participant sample
| Project | Author-described workflow | Implication |
| --- | --- | --- |
| Shipyard | Agents/gatekeeper, deploys, merges, SBOM, dashboard, approvals | Feature count, approvals and audit views are not sufficient distinctions |
| Steward Crew | Maintainer triage/review plus deterministic GitHub ledger | Maintainer assistance and controlled writes have public entries |
| CASCADE | Approved recovery, deterministic artifacts and execution receipts | A receipt alone is insufficient differentiation |
| Airlock | Cross-company incident investigation and selectively released evidence | Privacy-aware multi-agent incidents already have a strong example |
| Handover | Interview, sourced guide and onboarding across rooms | Knowledge handoff and sourced memory are covered |
| CrewPilot | Issue triage and approved fix plans | Planning alone leaves the final work unfinished |

Sources:
- https://github.com/Shrinet82/shipyard
- https://dev.to/therealjahaan/i-gave-my-open-source-project-an-ai-crew-that-cannot-touch-github-4729
- https://dev.to/yashshah1211/when-our-ai-agent-said-committed-before-it-had-executed-anything-21b2
- https://dev.to/martinez21/two-companies-one-outage-zero-shared-logs-building-airlock-on-switch-1e5h
- https://dev.to/pinnaclecrypt/handover-i-made-three-ai-agents-run-an-exit-interview-in-team-chat-57mf
- https://github.com/kamalesh404/CrewPilot

These observations do not establish validity as final entries, judge scores, production reliability or absent features. Do not call teams failures based on a README. A bounded public sample is not the whole competitive field.

## Established products
Amoeba describes sessions, ownership, shared commit-bound notes, approvals and takeover. CodeRabbit describes verification agents, behavioral analysis and rechecking fixes. LangGraph supports checkpointed interrupt/resume. GitHub checks are commit-bound. We need a useful end-to-end workflow, not claims that those primitives are absent elsewhere.

Sources: https://useamoeba.com/faq ; https://www.coderabbit.ai/review ; https://docs.langchain.com/oss/javascript/langgraph/thinking-in-langgraph

## Feature priorities
P0: counterfactual check. Same verifier-owned assertion fails for the expected reason on base and passes on candidate. Refuse a placebo check that passes both. Record repository CI as context, never sufficient proof.

P0: explain changed evidence. Full repo/base/candidate/check/harness/environment identities. Changed inputs show Evidence changed; old results remain historical. Unknown dependencies invalidate the full case.

P0: meaningful disagreement. Verifier challenges a specific behavior with an executable check or an explicit unresolved question. No third agent merely to debate.

P0: real Switch handoff. Human clarifies, two identities exchange repair/results, source message references remain visible.

P1: model-free replay. Execute frozen checks again with a new execution timestamp, without more model reasoning.

P1: actual budget panel. Elapsed time, invocations and reported cost when available. Unknown remains unknown. Limit whole-case AI invocations to three: one optional check proposal and two candidate attempts. Deterministic classification/replay use no model. CLI internal turns need provider enforcement; invocation caps alone do not guarantee dollar caps.

Stretch: selective rechecks only with explicit complete input manifests. Do not build a speculative dependency graph under the deadline.

## Edge-case matrix
| Input/condition | Required outcome |
| --- | --- |
| Candidate weakens its tests while source remains wrong | Frozen check rejects it |
| Candidate already meets agreed behavior and base passes too | INCONCLUSIVE, no false accusation |
| Check passes on original and candidate | INCONCLUSIVE: cannot establish the claimed fix |
| Named behavioral assertion fails on base; candidate/adjacent checks pass | VERIFIED for those exact inputs |
| Import/collection failure, zero tests, timeout, skip or missing report | INCONCLUSIVE, never a valid bug reproduction |
| Candidate config/conftest tries to bypass verifier | Independent harness unaffected; invalid report INCONCLUSIVE |
| Code/check/environment changed after a result | Evidence changed, previous result historical |
| Reconnect or duplicate transport sends | One action per stable command identity |
| Two competing candidate replies | Revision check rejects a silent overwrite |
| Agent/quoted text says approve | No human authorization |
| Repeated executions disagree | INCONCLUSIVE; retry pass does not establish a flaky fix |
| Provider limit, bridge offline, human absent | Stop with resumable state and a clear next action |
| Hash mismatch or missing artifact | No verified badge from summary alone |

Existing spec supplies the actual isolation, trusted base ancestry and sender/outbox rules. This is empirical evidence for a trusted local project, not formal proof or hostile multi-tenant execution.

## Evaluation protocol
Version a suite covering at least the first six outcome classes, with labels frozen before execution. Publish every fixture and outcome. Add a genuine live Switch demonstration. Add one attributed historical public bug only if reproduction is feasible; otherwise label controlled fixtures honestly.

Record expected/observed outcome, input identity, wall time, human waiting time separately, AI invocations, reported provider tokens/cost or unknown, and deterministic replay time. Always report denominators. Zero false VERIFIED labels in this suite is a target before measurement, not a general guarantee.

Repeat one accepted and one rejected deterministic case three times for timing; report median and machine/runtime details. Claim time saved only after a comparable measured manual baseline. Until then report runtime. Cost benefit is a hypothesis: less repeated review/reasoning. Do not fabricate salary-based ROI.

## Judge-facing story
Our target is a three-minute presentation, not a verified form limit:
- 0:00–0:20: show a real bug and a green but false candidate.
- 0:20–0:50: agree behavior through Switch and reproduce with frozen check.
- 0:50–1:40: targeted feedback -> fixing agent -> actual candidate and execution.
- 1:40–2:20: unchanged red/green check, adjacent behavior and exact revisions.
- 2:20–2:40: new candidate invalidates earlier evidence.
- 2:40–3:00: actual measurements, source-room trace, reproduction and limits.

Clearly label cuts, fixtures and playback. Do not imply a recorded run is live.

## Event and core contribution
Published dimensions: Switch use, execution, creativity/impact and presentation. Numeric weights remain unverified because extracted counters show zero. Blog evaluation emphasizes clarity, accuracy and usefulness to a first-time Switch user. Wispr needs actual usage evidence.

Core requires a hackathon-labelled issue assigned before work. Query for currently open unassigned issues returned no matches. Sentry #820 and Factory Droid #783 were inspected: both are assigned to others. Do not claim them. Overview says one person per issue while live issues show multiple assignees; maintainer clarification is needed before relying on a slot. No comment/claim has been sent. Main entry takes priority.

Sources:
- https://www.wemakedevs.org/hackathons/switch
- https://www.wemakedevs.org/hackathons/switch/resources
- https://github.com/sandbox-quantum/switch/issues/820
- https://github.com/sandbox-quantum/switch/issues/783
- https://github.com/sandbox-quantum/switch/blob/main/CONTRIBUTING.md

## Blog and deadline
Write an executable explanation, not promotion. Proposed title: Your CI Is Green. Your Bug Is Still There. Include the false candidate, check, real room messages, outputs, failed approaches, tested setup/troubleshooting, limitations and actual Wispr scorecard. Publish only after execution evidence exists. Registration/submission stays manual because the official rules prohibit automated participation.

## Cuts
No marketplace, universal connector gallery, chatty multi-model debate, billing, RAG/vector database, Kubernetes, speculative ROI, ornamental 3D graph or duplicate orchestration framework. The raw identity frames working evidence.
