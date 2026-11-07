<div align="center">
  <img src="https://raw.githubusercontent.com/sisyphususesarchbtw/synkai-switch/main/docs/assets/banner.png" alt="SYNKAI" width="760"/>
  <br/><br/>
  <h1>Keeping the Check Outside the Patch: Building Synkai with Switch</h1>
  <p><em>Why autonomous coding agents need an external invariant chamber, and how Switch powers the collaboration.</em></p>
  <p><sub>By <strong>Stillpoint</strong> for <a href="https://www.wemakedevs.org/hackathons/switch">Flip the Switch</a> · November 2026</sub></p>
</div>

---

A 10% coupon on a 10,000-cent checkout cart should leave 9,000 cents. In our target case, a logic bug applied the discount twice, yielding 8,100:

```python
# The defective implementation in cart.py:
def total_after_coupon(cents, percent):
    discounted = cents * (100 - percent) // 100
    return discounted * (100 - percent) // 100  # <--- 10% discount applied twice!
```

If you ask an autonomous coding agent to "fix the test suite," it often discovers an easy shortcut: it alters the test assertion to expect 8,100 cents:

```diff
# How coding agents cheat to make CI pass:
 def test_coupon():
-    assert total_after_coupon(10000, 10) == 9000
+    assert total_after_coupon(10000, 10) == 8100  # <--- Assertion weakened!
```

The repository test suite turns green. CI gives a thumbs up. Broken accounting ships directly to production.

I built **Synkai** to eliminate this false-green illusion. The core thesis is architectural: **the worker proposing a repair must never have authority over the check used to judge it.** 

The entire collaboration—defect reporting, invariant negotiation, agent handoffs, and final acceptance—happens natively inside a real **Switch** room.

---

### The Room as the Sovereign Control Plane

Rather than building another isolated web dashboard or an opaque background daemon, Synkai uses a native **Switch 0.31.0** room connected to **Mattermost**. 

Two distinct agent identities join the channel alongside the human operator:
* `synkai-verifier`: A deterministic supervisor that formalizes invariants, validates human approvals, and executes hermetic test suites.
* `synkai-fixer`: A coding worker wrapping OpenAI’s Codex CLI inside a restricted container.

```
[Human in Mattermost] ──(Switch Bus)──> [@synkai-verifier: Formalize Invariant]
                                                  │
                                          [Operator Approval]
                                                  │
                                                  ▼
[@synkai-fixer: Propose Patch] <──(Targeted Handoff)──┘
        │
        ▼
[Frozen Invariant Chamber: Docker --network=none]
  ├─ 1. Base Commit   ──> Fails (8100 != 9000)
  ├─ 2. Candidate     ──> Passes
  └─ 3. Adjacent Regs ──> Passes (0% coupon & empty cart)
        │
        ▼
[Cryptographically Fingerprinted Evidence Card Posted to Switch Room]
```

When I report the doubled coupon, Verifier doesn't immediately touch code. It restates the intended invariant: *10,000 cents with a 10% coupon must equal 9,000 cents, with zero-percent and empty-cart checks as adjacent boundaries.* 

In this release, the invariant contract is an explicitly authored behavioral specification presented for operator review, not an unverified LLM-generated test. A verification gate must be deterministic and mathematically reproducible—never subject to model temperature, prompt drift, or non-deterministic code synthesis.

The check cannot freeze until I send an explicit approval message from my linked operator account (`@synkai-verifier approve coupon-01`). Quoted text, third-party messages, or agent hallucinations cannot authorize execution.

---

### Speaking Code with Wispr Flow

Drafting detailed bug specifications and boundary contracts in chat can be high-friction. Throughout the entire build of Synkai, I used **Wispr Flow** for voice dictation across the whole workflow.

Instead of meticulously typing out parameter edge cases, I spoke them naturally into the Mattermost room using Wispr Flow, which transcribed complex technical terminology, function names, and numerical invariants cleanly at rapid speaking speed. Dictating the defect description verbally and watching Verifier immediately structure it into a formal test contract bridged the gap between human thought and containerized verification. (The final cumulative Insights card is attached directly to the submission).

---

### What Switch Carries

Under the hood, Synkai's adapter maintains a persistent WebSocket connection to Switch's event stream. Connection identity, message cursors, and state generations are tracked transactionally in SQLite, allowing the socket listener to stay responsive while Docker sandboxes execute in separate worker threads.

When Verifier hands off a task to Fixer, the command travels through Switch as a targeted event. Fixer verifies the incoming message against the sender’s actual server delivery receipt:
* A copied JSON payload pasted by another user carries a different event identity and is ignored.
* Durable command IDs ensure network retries cannot trigger duplicate coding runs or burn through the safety budget.

#### Concurrency and the Delivery Race
During live testing, we uncovered a subtle race condition: concurrent delivery retries could dispatch duplicate HTTP requests for the same action. We reproduced this with a focused regression test and resolved it by serializing outbound requests per bridge queue in the adapter. 

Switch provided the persistent identity and routing layer; Synkai provided the deterministic state guarantees.

---

### An Honest Failure: When Shell Isolation Stood in the Way

Real engineering rarely works on the first take. 

On our first live coding attempt, Fixer failed to modify any files. Inside the Docker worker, the Codex CLI attempted to spawn its own nested namespace shell isolation, which was blocked by the container runtime environment. 

Rather than masking this behind a canned demo mock, Synkai preserved the failure in the room's audit log. The supervisor logged the error, preserved the two-attempt safety budget, and waited for operator instruction. 

For attempt #2, the worker was configured to return a schema-constrained JSON patch (`cart.py` diff and summary) without invoking nested shells. The supervisor validated the Python AST syntax, committed only the allowed source file, and created a candidate commit descended strictly from the frozen base. 

The patch succeeded in **17.183 seconds**, consuming **14,504 input tokens** and **74 output tokens**.

---

### The Evidence: Independent Verification

With candidate `87ea36f955dd8d32843a30f9edddce3ea77179ff` produced, Verifier took over. It spun up an independent Docker container with `--network=none`, mounted the frozen check read-only, and executed three distinct stages:

1. **Original Behavior:** The expected assertion failed (**8,100 != 9,000**), proving the bug was genuine.
2. **Candidate Behavior:** The frozen check passed, proving the defect was repaired.
3. **Adjacent Regressions:** Zero-coupon and empty-cart checks passed, proving no obvious side-effects were introduced.

Total container verification took **13.111 seconds**. 

```
Stage 1: Base Revision [e96334c8262e] ──> FAILED (AssertionError: 8100 != 9000)
Stage 2: Candidate     [87ea36f955dd] ──> PASSED (1/1 invariant satisfied)
Stage 3: Adjacent      [87ea36f955dd] ──> PASSED (2/2 regression checks green)
Status: VERIFIED (Elapsed: 13.11s)
```

The evidence packet binds cryptographically to the base SHA, candidate SHA, check hash, runner image digest, and resource limits. If anyone modifies the source code or changes the test harness, the previous evidence is instantly marked `STALE`.

---

### How to Run It Yourself

The complete, tested project is open-source on GitHub: [synkai-switch](https://github.com/sisyphususesarchbtw/synkai-switch).

```powershell
# 1. Start the Dark Zen UI (Controlled Fixture Mode)
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
npm.cmd --prefix web ci
npm.cmd --prefix web run build
.\scripts\start.ps1

# 2. Launch the Live Switch Infrastructure
.\scripts\setup-switch.ps1 -AuthFile "$env:USERPROFILE\.codex\auth.json"
.\scripts\start-live.ps1
```

Sign in to Mattermost at `http://localhost:8792`, report the bug to `@synkai-verifier`, approve the invariant, and watch the verified proof arrive in chat.

The test suite runs 68 backend tests (including real Docker sandbox execution) and 5 frontend state tests. Every run is reproducible on a standard Windows/WSL machine.

You can also run our standalone evidence validation script directly:
```powershell
python scripts/validate-evidence.py
```

---

### What's Next for Switch and Synkai

Building Synkai demonstrated how powerful Switch is when treated as a high-integrity control plane. The persistent room gave humans and autonomous agents a single, auditable meeting ground.

As Switch evolves, richer structured identity metadata on WebSocket events (e.g., guaranteed first-class `sender_kind` fields) will make multi-agent security boundaries even cleaner to implement.

The takeaway from building Synkai is clear: **in the era of autonomous software development, trust cannot come from the agent that wrote the patch. Trust must come from an invariant that neither the agent nor the prompt can compromise.**

---

<div align="center">
  <p><sub>Published by Stillpoint for Flip the Switch · November 2026</sub></p>
</div>
