# NYKT

**Clarity, earned.**

A Switch collaboration room for verifying AI-written bug fixes.

Built solo by **Stillpoint** for the Flip the Switch Hackathon, November 4–7, 2026.

[GitHub repository](https://github.com/sisyphususesarchbtw/nykt-switch)

## Status

Planning repository. Product implementation has not started. There is no working integration, verification runner, or UI yet. Documentation describes the intended build; it is not a claim of shipped capability.

## The problem

A green test suite does not necessarily demonstrate that a reported bug was fixed. An agent can change the test, fail to reproduce the original behavior, or report a result from an older patch. NYKT is designed to turn a claimed fix into a small, inspectable evidence packet.

## Intended workflow

1. A person confirms expected behavior in team chat through Switch.
2. A verifier freezes a behavioral check and reproduces the defect on the original revision.
3. A fixing agent proposes a patch in a separate workspace.
4. An independent runner executes the unchanged check on both revisions.
5. The person reviews evidence, uncertainties, and the resulting patch.

Switch carries the real collaboration and agent handoffs. NYKT's UI will show the case state and evidence, with a link back to its source room.

**A verified result applies only to the recorded check, environment, and revisions. It is not a guarantee of general correctness or security.**

## Build documents

- [Product brief](PRODUCT.md)
- [Visual direction](DESIGN.md)
- [Design specification](docs/superpowers/specs/2026-11-06-nykt-design.md)
- [Implementation plan](docs/superpowers/plans/2026-11-06-nykt.md)
- [Task board](TASKS.md)
- [Logo prompt](assets/brand/LOGO-PROMPT.md)
- [Build journal](docs/build-journal.md)
- [Blog draft](docs/blog.md)
- [Submission checklist](docs/submission.md)

## Entries

Best Business Workflow, Code with Wispr, and Best Blog. Wispr usage evidence will come from actual Insights data. No submission has been made.

## Inspiration

[Switch](https://docs.switchagents.ai/), [Amoeba](https://useamoeba.com/), [Ryoku](https://ryoku.dev/), and [Hermes Agent](https://hermes-agent.nousresearch.com/). NYKT is an independent hackathon project and is not affiliated with these products.

Setup instructions and a real demo will be added after their steps have been tested.
