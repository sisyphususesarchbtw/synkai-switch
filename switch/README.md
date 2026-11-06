# The actual Switch integration

Transport: bundled **Mattermost**, Switch server **0.31.0**, released Console source tag `switch-console-v0.40.1`, commit `6ab2ff463ad9518920ba2a15b182b1d2e760fd9f`. The adapter uses the observed WebSocket protocol and HTTP operations, declaring protocol 8. The event website's older SSE description is not the implementation used here.

| Participant | Responsibility | Access |
| --- | --- | --- |
| Operator | Reports, approves the check, reviews/accepts a patch | Exact linked Mattermost sender allowlisted locally |
| `synkai-fixer` | Receives targeted repair handoffs; wraps Codex source proposals | Candidate workspace and explicitly selected read-only Codex login |
| `synkai-verifier` | Proposes behavior, records approval, runs checks, posts evidence | Harness and runner controlled by the local supervisor |

Both identities belong to the same operator. Their default addressing policy permits their owner and the owner's agents. One room has explicit workflow instructions. Each handoff carries a stable command ID; the receiver matches it to the sender's actual HTTP event receipt, rather than trusting copied JSON or a display name. Operator approval is anchored to an exact room, linked transport identity and addressed message.

A GitHub room reference points to the implementation. A verifier-authored document records behavior, original SHA, frozen check hash and approval message ID. Those provide collaboration context; the separately frozen local harness enforces the execution boundary. The model worker receives neither Switch keys nor verifier files.

SQLite retains connection ID, cursor, generation, incoming work and outgoing delivery state. Concurrent sends are serialized; duplicate commands cannot reserve another attempt. A lost HTTP response after server acceptance can still duplicate a chat post on retry. Stable command deduplication protects coding work: this is at-least-once delivery, not an exactly-once transport claim.

Follow the [root README](../README.md) or [setup guide](../docs/setup.md). Private configuration remains in ignored `.local/switch/`. Start with `python -m synkai --config .local/switch/runtime-config.json`.

There is one language-model provider behind Fixer. Verifier's approval validation and result classification are deterministic. Two Switch identities are not counted as two independent language models.
