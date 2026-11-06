# Switch hackathon opportunity analysis

Historical research snapshot. Naming and visual proposals below are superseded by ../../PRODUCT.md and ../../DESIGN.md: the current product is Synkai, team Stillpoint, with a raw monochrome/engraved interface. The latest competitor review and evaluation matrix are in ../strategy-and-evaluation.md. Preserve the original alternatives as research context, not current requirements.

Research date: November 6, 2026, IST.
Status: research and proposed direction; no product direction or implementation approved.

## Recommendation

Enter Best Business Workflow with a narrow, evidence-first bug-fix verification workflow. Working name: Pramana (name and linguistic/brand validation pending). People define intended behavior in a Switch room; a fixing agent proposes a patch; a separate verifier runs a frozen regression check against the base and patched revisions. The result is an inspectable evidence packet, not a general correctness guarantee.

This recommendation is based on problem clarity, demonstrability, deadline feasibility, and relevance to human-agent collaboration. It is not a statistical prediction of winning. Entrant numbers and competitive submissions are unknown.

## What the event demands

- At least one person and one agent complete a real task through Switch in team chat.
- Switch must be central; README must explain its role.
- Existing agents and libraries are allowed; Switch setup and workflow must be built during the event.
- Submission deadline: November 7, 2026, 11:59 PM IST.
- Main evaluation dimensions: use of Switch, technical execution, creativity/impact, presentation. The text extraction displayed animated values as 0%; actual weights remain unverified.
- Core contribution requires a hackathon-labelled issue assigned before work; PR open by the deadline. Overview has inconsistent 20-versus-10 winner counts.
- Confirm final upload fields, video constraints, repository visibility, and entry eligibility before submission. Overview's broad participation wording is qualified by official rules.

Sources: https://www.wemakedevs.org/hackathons/switch and https://www.wemakedevs.org/hackathons/switch/rules

## Firsthand developer complaints

These are qualitative signals from a small purposive public sample, not representative market research. Product promotion occurs in some discussions; avoid treating every post as independent customer demand.

1. Review noise: developers report spending time answering speculative AI nitpicks instead of fixing demonstrated defects.
   https://www.reddit.com/r/softwaredevelopment/comments/1vib1yh/my_coworkers_are_using_ai_agents_to_review_prs/
2. Weak tests: developers report agents changing assertions or skipping tests to achieve a green run while behavior remains wrong.
   https://www.reddit.com/r/ChatGPTCoding/comments/1wldasi/when_a_test_fails_coding_agents_fix_the_test_the/
3. Meaningless green checks and excessive test execution: developers question tests that pass while the feature still fails.
   https://www.reddit.com/r/Agentic_Coding/comments/1wce8p7/why_does_ai_write_tests_that_dont_actually_test/
4. CI waiting and context switching: repeated slow runs interrupt development and make diagnosis frustrating.
   https://www.reddit.com/r/devops/comments/1rrvqyt/the_cicd_feedback_loop_from_hell_push_wait_8_min/
5. GitHub independently recommends tests that fail before a claimed bug fix and warns about CI weakening.
   https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/

## Competitive landscape

| Existing solution | What it already provides | Implication for our proposal |
| --- | --- | --- |
| Claude Code in Slack | Coding delegation from conversation, context gathering, progress and PR flow | A chat-to-PR bot alone is insufficient differentiation |
| CodeRabbit | Review, behavior and coverage analysis, verification agents, developer interactions | Verification and multiple agents are established capabilities; do not claim otherwise |
| Trunk | Flaky-test management, integrations, and advertised AI autofix beta | CI/flaky-test automation is crowded and needs historical data |
| Jam | Rich bug recordings and context, agent tooling and fix-verification artifacts | Capturing a report is not a distinct enough product by itself |
| n8n | Human review of agent tool calls across chat platforms | Approval buttons alone are not novel |
| Bump.sh / oasdiff | API diffs, breaking-change detection, CI gates and review/approval features | Avoid making a basic API-change approval tool |

Primary sources:
- https://code.claude.com/docs/en/slack
- https://www.coderabbit.ai/review
- https://trunk.io/roadmap?campaign=valentines2026
- https://github.com/trunk-io
- https://jam.dev/resolve
- https://blog.n8n.io/production-ai-playbook-human-oversight/
- https://docs.bump.sh/help/api-change-management/
- https://www.oasdiff.com/

Potential gap is a product hypothesis: an explicit agreement on intended behavior, frozen executable evidence, agent disagreement visible to the person, and a compact decision record in the team's existing room. We have not established that competitors cannot implement this or that customers will pay for it.

## Approaches to compare with the user

A. Evidence-first bug-fix verification room — recommended. Highly demonstrable before/after result; bounded deterministic bugs make a feasible first scope. Risk: human-approved checks can still encode a mistaken requirement.

B. CI failure triage room. Collect failure context, reproduce, distinguish product/test/environment problems, propose the next action. Strong pain evidence, but dependencies and historical flakiness can swamp a short build. One successful retry does not establish flakiness.

C. API release readiness room. Coordinate contract changes, client impact, docs and owner decisions. Strong business story, but existing API products cover much of the obvious functionality, and realistic consumers add setup.

Do not develop all three. Choose one workflow, one stack, one chat bridge, and one convincing demo.

## Proposed workflow for approach A

1. Human supplies a bug report and candidate patch in the Switch room.
2. Verifier restates expected behavior and asks the human to settle any material ambiguity.
3. Freeze the approved check, harness and environment. Associate them with exact code revisions.
4. Run the same check against base and candidate in a separate runner the fixing agent cannot modify.
5. Require the expected behavioral assertion to fail on base and pass on candidate. Import failure, timeout or unavailable environment is inconclusive, not valid reproduction evidence.
6. Check adjacent behavior using a small, relevant regression set; identify changed/skipped/removed tests and config changes.
7. If verification fails, the fixing agent receives the evidence through Switch and proposes a bounded repair. Freeze a new candidate revision and rerun.
8. Publish an evidence packet: behavior agreed, base/candidate revisions, check/harness identity, environment, commands, outputs, remaining uncertainty and human decision.

The verifier must have separate execution permissions and artifacts. Merely prompting two agents to be independent is insufficient. A new commit invalidates the old candidate's verification. The packet supports a review decision; it does not prove absence of all bugs.

Switch owns the actual collaborative path: incoming request, clarification, targeted agent handoff, repair request, evidence return, and human decision. The custom UI projects that workflow and opens its source thread; it must not conceal a separate backend orchestration path that bypasses Switch.

## Demonstration proposal

Use a small deterministic Python/pytest API or library fixture; stack is a proposal, not a user decision. A bug-fix candidate weakens a test without fixing behavior. The verifier's frozen check still fails. The human confirms the intended behavior, the fixing agent repairs production logic, and the exact check fails on base and passes on the repaired revision. Show real outputs and links. Label controlled fixtures honestly.

Include honest inconclusive handling: missing dependencies, checks that pass on both versions, or unrelated failures cannot produce a verified badge.

## Efficiency principles

- Use deterministic execution for pass/fail; use the model for interpretation and bounded repair.
- Two agent roles, with a person making decisions where intent is ambiguous.
- Select relevant checks first; bound runtime and repair attempts.
- Reuse evidence only when code, check, environment and configuration identities match.
- One actionable message per stage; detailed logs expand on demand.
- Measure runtime, model calls/cost, human interventions, supported-case outcome and false verified results on negative fixtures.
- Never present hypothetical savings or selected demo outcomes as measured production improvement.

## Preliminary visual direction

Interpret Hermes as Nous Research's Hermes Agent pending the user's clarification. Reference is operator simplicity, not a claimed pixel match.

Proposed identity: quiet scholarly workspace combining Greek proportion, Zen restraint and subtle Indian manuscript/astronomical geometry. Keep practical labels such as Evidence, Runs, Needs input and Verified. Mythological influence belongs in the mark, palette and restrained details, not in cryptic task names.

Warm limestone background, ink foreground, muted bronze/saffron accent, restrained vermilion for failure and moss for success. Use accessible contrast and text/icon status in addition to color. Optional dark theme is stretch work.

Single case workspace: compact case list, current question/action and evidence in the main view, contextual Switch thread accessible alongside. Lead with what needs the person's attention. Avoid ornamental dashboard charts, an agent aquarium, neon gradients, persistent particles, and deity illustrations in operational screens.

Small serif display treatment for identity; highly readable sans-serif for operations; monospace only for evidence. Short, purposeful motion; no streaming-text layout jumps; honor reduced-motion preferences. No visual mockup created yet.

## Task list

### Research and decisions
- [x] Read event overview, rules and resources.
- [x] Review firsthand complaints and primary competitor descriptions.
- [x] Compare three candidate directions.
- [x] Propose track, judging evidence, UI principles and bounded scope.
- [ ] User chooses the problem/approach.
- [ ] Validate against 2–3 existing public bug-fix cases and distinguish invented fixtures from historical cases.
- [ ] Confirm bridge, available agent access, Docker/Windows feasibility, team size and remaining build time.
- [ ] Confirm final submission fields and any actual rubric weights.
- [ ] Confirm Hermes reference and choose a visual direction using mockups.
- [ ] Write and approve the selected design, then prepare the implementation plan.

### Proposed build backlog, only after selection and design
- [ ] Get a real person-to-agent reply through Switch first.
- [ ] Establish two agent identities and targeted handoff behavior.
- [ ] Implement one reproducible verification runner and immutable evidence record.
- [ ] Handle accepted, rejected and inconclusive outcomes, plus stale candidate revisions.
- [ ] Demonstrate one false fix rejected and one actual fix verified.
- [ ] Build the minimal case/evidence interface and source-thread navigation.
- [ ] Verify duplicate events and bounded repair behavior.
- [ ] Check setup from a clean environment and document limitations.
- [ ] Record a concise real demo and publish reproducible setup instructions.
- [ ] Submit primary track; add blog/Wispr only if their requirements are actually met.

## Decisions still open

Problem selection; first supported language; incoming report versus existing PR; local fixture versus connected repository; chat bridge; precise approval/decision controls; whether the custom UI fits the remaining time; final name and visual reference. No implementation has started.
