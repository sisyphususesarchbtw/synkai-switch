# Synkai
Product: Synkai. Team: Stillpoint. Plain descriptor: a collaboration room for checking AI-written fixes.

The participant supplied the name, logo and visual references. Treat “a collective of cooperating agents” as the intended brand meaning, not a literal ancient translation. Greek kai means “and”; do not describe it as Greek for association. Existing AI businesses use Synkai/SynkAI, so use synkai-switch as the qualified repository identity. NYKT, Sakshi and Pramana are superseded.

## Problem and audience
Developers reviewing agent-written fixes need evidence that the patch addresses the agreed behavior, that checks were not weakened, and which revision the evidence covers. Initial user is a solo developer coordinating Fixer and Verifier through Switch; later the same room can serve a team.

## Competitive focus
Hook: Your CI is green. Your bug is still there.
USP: the unchanged verifier-controlled check must detect the original defect, pass on the candidate and remain tied to exact code/environment identities. A person can inspect the whole argument in one room.

Supporting features: turn agent disagreement into an executable check or explicit unanswered question; expire evidence on changed inputs; rerun deterministic checks without more model calls; bound repair attempts. Red/green testing, commit-bound CI and approval invalidation already exist. We claim a focused product combination, not exclusive technical novelty.

## Scope
One trusted local operator, one allowlisted Python repository, pytest, one active verification, two agent identities and one real bridge. Mattermost first; Discord after core acceptance. Slack/Telegram are later. No WhatsApp integration promise.

Switch carries clarification, targeted handoff, feedback and evidence return. A person approves intended behavior and the frozen check; Fixer works in a separately restricted workspace; Verifier owns the check bundle and runner. A candidate cannot alter the checks against which it is evaluated.

VERIFIED means the named behavioral assertion failed for the expected reason on base, passed on candidate, and required adjacent checks passed. REJECTED means executable evidence disproves the candidate. INCONCLUSIVE covers setup/error/timeout/zero collection/skipped checks, a check passing on both versions and insufficient evidence. STALE marks evidence whose inputs changed. Verification supports a review decision; it is not a general correctness guarantee.

## Boundaries and scale
No new IDE, general agent OS, marketplace, vector store, billing, Kubernetes, or second orchestration framework. Start with SQLite and bounded local workers. Keep narrow bridge/provider/runner/evidence interfaces; add queue, Postgres, object storage and project isolation when demand requires them. Hostile multi-tenant execution needs a separate design.

## Success and evidence
Reject a false fix with green repository tests; verify a real fix with the unchanged check; refuse a placebo check; expire stale results; preserve the actual source-room trail; reproduce setup from a clean clone. Publish the acceptance matrix and measured runtime/model usage. No invented savings, customers, confidence scores or win probability.

Detailed strategy, competitor sources, outcomes and metrics: docs/strategy-and-evaluation.md.
