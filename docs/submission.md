# Submission copy

Use the authenticated [submission form](https://www.wemakedevs.org/hackathons/switch/submit). The user must perform the actual entry; event rules prohibit automated submissions. The form can be edited until the deadline. Confirm personal eligibility and registration yourself. Never submit private local credentials.

## Project title

Synkai — Independent evidence for agent-written fixes

## Tracks

**Best Business Workflow.** Add **Best Blog** using the published build article. Code with Wispr consideration requires the genuine Insights usage card. Do not enter Best Core Contribution: this application repository PR is not an eligible assigned Switch-core contribution. Avoid splitting the same developer workflow across both main categories.

## Project description

Synkai helps developers turn a bug report into a repair they can review against an agreed behavior. In a real Switch/Mattermost room, an operator reports a defect and approves a concrete check. Fixer uses Codex to propose a source change; Verifier independently runs the same frozen check on the original and candidate, plus adjacent behavior. The patch-producing worker cannot edit that check.

The workspace shows real room activity, the pending human decision, the actual Git patch and exact execution evidence. Results bind to the original revision, candidate, check digest and runner image; changed inputs expire current evidence. Receipt-bound handoffs and a persisted two-attempt budget protect the collaboration from copied commands and duplicate work.

The demonstrated checkout example is deliberately authored. A 10% coupon was applied twice; the live model-proposed repair passed the unchanged behavioral and adjacent checks after the original reproduced the expected failure. The successful coding attempt took 17.183 seconds and verification 13.111 seconds on the local machine. An earlier failed attempt remains recorded. These are single observations, not general reliability or savings claims. This release supports the supplied small Python project and one local operator.

## GitHub repository

https://github.com/sisyphususesarchbtw/synkai-switch

Verify that the public default branch contains the tested product before entering it.

## Demo video

Required: a public/unlisted YouTube or Loom link under three minutes. Use [the finished recording script](https://github.com/sisyphususesarchbtw/synkai-switch/blob/main/docs/demo-script.md). **A hosted video link is still required; do not enter a placeholder or claim submission is complete without it.**

## Live demo

Leave blank. The operational app runs locally; no publicly hosted backend is claimed. A GitHub README or screenshot is not a live deployment.

## Blog

The finished [build article](https://github.com/sisyphususesarchbtw/synkai-switch/blob/main/docs/building-synkai.md) is in this public repository. Its rendered public URL after release is:

https://github.com/sisyphususesarchbtw/synkai-switch/blob/main/docs/building-synkai.md

For a dedicated blog platform, publish the same finished article in the user's account and use that public URL. Do not invent a published external post.

## Wispr usage card

Upload the genuine exported Insights card. See [capture steps](demo-script.md#wispr-side-entry). Text stats alone do not meet the upload requirement.

## How did you use Switch?

I connected two custom Python-supervised agent identities, synkai-fixer and synkai-verifier, to Switch server 0.31.0 and its bundled Mattermost bridge. Fixer wraps authenticated Codex CLI in a restricted Docker worker. Verifier deterministically validates approvals, freezes checks, runs independent verification and posts evidence. I'm the solo human operator; there are no invented teammates or extra model agents.

Switch is the collaboration path: the operator's addressed report and approval arrive as room events; Verifier sends a targeted handoff to Fixer; Fixer returns a real candidate commit; Verifier posts the result for review and acceptance. Room instructions define responsibilities, a GitHub reference locates implementation context, and a verifier-authored room document retains the agreed behavior and check identity.

The adapter persists WebSocket connection identity/cursors and command delivery state. Handoffs are matched to actual sender receipts. The coding worker receives neither Switch API keys nor the verifier harness. Synkai's browser workspace projects this real collaboration and immutable execution evidence; approvals remain in the source conversation. Only Mattermost is demonstrated in this release.

## What did you like, and what would you improve?

Switch gave the human and both agent identities one persistent room with targeted handoffs, shared instructions, references and documents. The operation catalogue made the released integration discoverable, and keeping decisions in chat made the patch's approval trail inspectable.

I would improve version-matched examples: the event overview described SSE, while the release I used exposes WebSocket events. Some incoming human and agent messages had null sender_kind, so I used exact linked operator identities and receipt-bound handoffs instead of relying on display names or that field. Clearer typed identities and documented delivery/idempotency behavior would make trustworthy integrations easier to build. These comments describe this observed release, not every Switch deployment.

## Final manual check

- Public default branch has the application, setup, evidence and article.
- Public/unlisted video opens signed out, is under 3 minutes and shows real chat.
- Genuine Wispr card uploaded if entering that side award.
- Blog URL opens publicly; optional social-post URL only if actually published.
- Core PR field left blank unless an eligible Switch-core contribution genuinely exists.
- User submits, verifies confirmation, and keeps its receipt. No submission has occurred merely because these files exist.
