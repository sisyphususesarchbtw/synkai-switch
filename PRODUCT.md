# NYKT product brief

## Identity

Product: NYKT (pronounced "nikt"). Team: Stillpoint. Tagline: Clarity, earned.
NYKT is a coined name inspired by the sound of Nyx and a nocturnal atmosphere; do not invent a Greek translation. This is a project naming decision, not a claim of trademark or domain availability. Sakshi is rejected; Pramana is retired.

## Audience and problem

Developers reviewing agent-written fixes need to know whether the proposed patch addresses the reported behavior, whether the checks were weakened, and which revision the evidence covers. Initial user is a solo developer coordinating a fixing agent and a verifier; the same workflow can later serve a team.

## Mechanism

A person agrees on intended behavior through Switch. The verifier freezes a check before repair; the fixing agent can change source in its own candidate workspace but cannot alter the verifier's check bundle or runner. Exact check execution on base and candidate generates inspectable evidence. A candidate change makes old evidence stale.

## Scope

One trusted local workspace, one allowlisted Python repository, pytest, one active case, two agent identities, and one real chat bridge. Mattermost is the default because Switch's local setup supplies it. Discord is an optional second bridge after the workflow works. Slack and Telegram are future adapters. WhatsApp is not promised by the event's listed bridge set.

The product is not a coding IDE, a general multi-agent platform, a full CI service, a formal proof engine, or a production auto-merge bot. Repository publishing is part of project maintenance; verification does not automatically merge or deploy anything.

## Outcomes

VERIFIED means the frozen behavioral assertion failed as expected on base, passed on candidate, and required regression checks passed. REJECTED means an executable behavioral or regression check disproves the candidate. INCONCLUSIVE covers setup failure, unknown assertion failure, timeout, collection failure, skipped checks, a check passing on both versions, or insufficient evidence. STALE means code or verification inputs changed after evidence was produced.

## Proposed scale path

Start with SQLite and bounded local workers. Introduce a durable job queue, Postgres, object storage and per-project identity only when multiple projects require them. Runner isolation, idempotent events, immutable input identities and provider/bridge adapters are useful boundaries from day one. Hosted multi-tenant execution is a later product with a separate security design, not a property of the MVP.

## Success

Reject a false fix that only weakens the repository tests; verify a real fix using an unchanged behavioral check; show an inconclusive execution honestly; preserve a source-room trail a judge can follow; reproduce setup from a clean clone.

## Evidence

Research and source links live in docs/research. Public reports are qualitative signals, not a representative survey or proof of demand. Report measured runtime and model usage only after implementation. No fabricated savings, customers, votes, or success rates.
