# Evaluation

Can an operator agree a behavior in a real Switch room, receive an actual model-proposed repair, and inspect an independent check that reproduces the defect before passing the candidate?

## Observed November 6, 2026

| Check | Observation |
| --- | --- |
| Report | Operator posted the doubled-coupon report in Mattermost; an addressed Switch event was captured |
| Approval | Exact operator message `sw_4bfed92279d18e1fe5a1106ed9eb568e` |
| First attempt | Stopped before changing source: nested shell isolation could not create a namespace |
| Retry | Operator explicitly delegated the retry in Codex chat; the real room recorded its assistant-sent origin |
| Actual candidate | `87ea36f955dd8d32843a30f9edddce3ea77179ff`, created from the model's structured proposal |
| Original | Expected assertion failed: 8100 versus 9000 |
| Candidate | Same frozen check passed |
| Adjacent | Zero-percent and empty-cart checks both passed |
| Successful proposal | 17.183 seconds; CLI-reported 14504 input and 74 output tokens |
| Independent verification | 13.111 seconds, three recorded stages |
| Monetary cost | Unreported |

This is one successful live case, an earlier failed coding attempt, and two separate authored control candidates. These are not a success-rate benchmark, customer validation or claimed financial savings. Successful-attempt duration excludes the failed attempt, setup and operator time.

[Live record](evidence/live-switch-run.json) · [Actual patch](evidence/live-candidate.patch) · [Git bundle](evidence/live-candidate.bundle). The [controlled Docker record](evidence/controlled-docker-run.json) separately shows the test-only false fix rejected and an authored repair verified, with zero model calls.

## Failure coverage

Tests cover quoted/agent/wrong-room approvals, unaddressed messages, copied commands without sender receipts, duplicate/concurrent delivery, durable cursors and registration reuse, budget exhaustion, process locking, interruption, unrelated ancestry, file/tree allowlists, candidate test/config attacks, a check already passing on base, setup/runtime errors, stale identities, contradictory replays, persistence and browser-origin/session protection.

The local full run passed 76 backend tests (77 with real Docker), 5 UI logic tests and the production build. An upstream Starlette TestClient/httpx warning remains visible. Negative tests verify fail-closed validation on tampered digests, fingerprints, invalid stage progressions and missing files.

## Limits

The check is authored, not inferred from arbitrary language. The release supports one dependency-light checkout project and one operator, with one model provider behind two Switch identities. It does not establish general bug-fixing ability, hostile-code service safety or superiority over other teams. No outside developer testimonial has been collected.

The demonstrated distinction is the boundary: a human approves a check that the patch-producing worker cannot alter, then receives before/after evidence tied to immutable inputs. Switch retains the conversation and handoff provenance around that boundary. The next useful validation is an outside developer reproducing setup and supplying a separately authored behavioral case.
