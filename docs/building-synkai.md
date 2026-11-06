# Keeping the check outside the patch: building Synkai with Switch

A 10% coupon on a 10000-cent cart should leave 9000 cents. Our example applied it twice and returned 8100. A patch can make its own test green by changing the expected answer to 8100. The original behavior would still be wrong.

I built Synkai around a concrete agreement: the operator approves the behavior, the coding worker proposes a patch, and a separate verifier checks both revisions against the same frozen check. The conversation, decision and handoffs stay in a real Switch room.

Synkai is a solo hackathon project under the team name Stillpoint. I used coding assistance during implementation and Wispr Flow for dictation. The checkout defect and independent check are deliberately authored examples, not customer data or evidence of general autonomous bug fixing.

## The room is part of the workflow

Two Switch identities join a bundled Mattermost channel: `synkai-fixer` and `synkai-verifier`. Fixer wraps Codex CLI; Verifier is a deterministic supervisor that validates operator decisions and executes checks. Two identities do not mean two independent language models.

The operator reports the doubled coupon and asks Verifier to propose the expected behavior before acting. The proposal says that 10000 cents with a 10% coupon must become 9000 exactly once, with zero-percent and empty-cart checks as adjacent cases. Approval is an exact addressed message from the configured linked Mattermost account. A quoted approval or an agent's claim that the user approved cannot freeze the check.

Room instructions explain the division of work. A GitHub reference points to the implementation, and a verifier-authored room document retains the approved behavior, base revision, check digest and approval message ID. These make the shared agreement discoverable. The actual security boundary is the separately frozen local check bundle; room context alone does not enforce isolation.

## What Switch carries

The adapter uses the released server's WebSocket event stream and HTTP operations. It persists connection identity, cursor and generation in SQLite. Socket readers remain responsive while coding or container execution happens in separate worker threads.

Verifier sends a targeted repair handoff through Switch. The recipient matches its incoming message to the sender's actual delivery receipt. A copied JSON command in another message has a different event identity and cannot authorize work. Durable command IDs prevent a replay from reserving another coding attempt.

I found a race during the real run: the sender and background delivery retry could post one action concurrently. A regression test reproduced two HTTP requests for the same action. Serializing sends per bridge made that test pass with one request. A lost response after server acceptance can still duplicate a chat post; the implementation does not claim exactly-once network delivery. The persisted coding budget is protected separately.

## A failure changed the coding method

The first actual coding attempt made no source change. Inside Docker, the CLI tried to start its nested shell isolation and failed because it could not create a namespace. Keeping that failure was more useful than hiding it behind a canned successful patch.

For the remaining attempt, the worker received the complete small source snapshot and returned schema-constrained JSON: replacement `cart.py` and a short summary. It was instructed to use no tools or shell commands. The supervisor validated the proposal's shape and Python syntax, wrote only `cart.py`, and created a commit descended from the frozen base. Candidate code never ran on the Windows host.

The CLI's sandbox stayed enabled. Its existing login file was mounted read-only with explicit operator permission; Switch credentials, the verifier harness, other home files and the Docker socket were not mounted. Read-only authentication still means the credential is readable inside that worker, a scope that setup documents clearly.

The operator explicitly delegated the retry through Codex chat. The assistant sent the real Mattermost command and recorded that origin. We did not fabricate a human event or reset the two-attempt budget.

## The evidence

The successful model proposal removed the second coupon application. The supervisor created candidate `87ea36f955dd8d32843a30f9edddce3ea77179ff`.

Verifier then ran three separate stages with the same frozen check and recorded image:

1. Original behavior: the expected assertion failed, 8100 versus 9000.
2. Candidate behavior: the check passed.
3. Adjacent behavior: zero-percent coupon and empty cart both passed.

The successful coding attempt took 17.183 seconds; verification took 13.111 seconds. These are single local measurements, excluding the failed attempt and setup/operator time. The CLI reported 14504 input tokens and 74 output tokens for the successful proposal. It did not report a monetary cost, so I make no dollar-savings claim.

The workspace shows the actual patch, received room activity, connection state, pending operator action and raw execution record. A verified result is distinct from operator acceptance. Evidence is bound to base, candidate, check and image identities. Changing inputs makes the previous result historical; contradictory replays remain inconclusive.

## Run it yourself

The [repository README](../README.md) contains the full setup. Install the committed Python/Node dependencies, build the interface, and run the verifier/coding images. The setup script downloads the official commit-pinned Switch Compose file, verifies its digest and starts server 0.31.0 with bundled Mattermost on loopback.

```powershell
.\scripts\setup-switch.ps1 -AuthFile "$env:USERPROFILE\.codex\auth.json"
# Separate terminals:
.\scripts\start-live.ps1
.\scripts\start.ps1
```

Sign in using the generated private local login file. Report the coupon defect, approve the proposed behavior in the room, inspect the patch and checks, then accept it if satisfied. Existing credentials and agent registrations survive setup restarts. A separate labelled fixture view also demonstrates a deliberately weakened-test false fix being rejected without calling a model.

The public repository includes the real patch, a two-commit Git bundle, redacted execution evidence and the independent harness. Local verification passed 68 backend tests including Docker execution, five UI logic tests and the production build. [Evaluation](evaluation.md) describes the limits and provenance.

Final long-running checks also exposed database connections being left to later cleanup after transactions. I added explicit closure and regression checks for all three state stores, then reran the full suite. The recorded video reflects the earlier 65-test checkpoint; the release now passes 68 backend tests.

## What I would improve next

The released API operation catalogue helped resolve differences between older event documentation and the running server. The next improvements I want from Switch are version-matched integration examples and clearer structured identity information in incoming human/agent events; the observed `sender_kind` was null, so Synkai uses an exact linked operator identity and receipt-bound handoffs instead.

Synkai currently supports one authored dependency-light Python project and one operator. The next validation is an outside developer reproducing setup and supplying a new behavioral case. General repository support should follow that evidence. The part worth preserving is already concrete: a patch-producing worker cannot rewrite the agreement used to judge its repair.
