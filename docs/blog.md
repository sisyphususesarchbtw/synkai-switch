# Your CI Is Green. Your Bug Is Still There: Building Synkai with Switch

Status: editorial draft based on design decisions. Not yet a build report. Do not publish as a completed project until the evidence sections are written from actual execution.

## The question

When an AI coding agent says it fixed a bug, what would make that claim worth trusting? A successful test run helps, but only if those tests actually exercise the reported behavior and the candidate did not quietly change the checks.

## The workflow we are building

Synkai brings a developer, a fixing agent and a verifier into a Switch room. The person resolves ambiguity about the behavior. The verifier freezes a small check. The fixer proposes a candidate. The same check runs on the old and new code, producing an evidence packet that the person can inspect. The strongest opening will be an actual false candidate with passing repository tests and a still-failing independent check.

That packet is deliberately narrow. It describes what was checked, against which revisions, in which environment, with what result. It does not certify that all other behavior is correct.

## Why collaboration matters

The human contributes intent, the fixing agent contributes a patch, and the verifier contributes execution evidence. Switch is intended to carry the clarification, targeted handoff, repair request and evidence return in the same room. This is the part the final demo must show actually working.

## Build evidence to add before publication

- The exact tested Switch version and room setup, including any Windows issues.
- A real false fix and the unchanged check that rejects it.
- The real patch, base/candidate SHAs and red/green outputs.
- A setup failure or uncertainty the system handled honestly.
- Measured runtime/model usage and the limits of those measurements.
- What speaking with Wispr changed about prompts, instructions and documentation; include actual Insights scorecard, not a fabricated score.
- Screenshots, runnable setup, GitHub link and demo link.

## Lessons to write after the build

Explain which assumptions were wrong, what scope was removed, where the verifier's independence begins and ends, and why the team picked one usable workflow over a broader platform. Keep this section factual rather than predicting success.

## Reference material

- https://www.wemakedevs.org/hackathons/switch
- https://docs.switchagents.ai/switch-rooms/internals/agent-protocol
- https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/
- https://useamoeba.com/faq
