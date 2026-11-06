# NYKT visual direction

Status: implementation direction; no screen mockup or final logo has been approved or built.
Mode: Operate. Primary scene: reviewing one disputed bug fix at a desk.

## Dark Zen architecture

Near-black basalt, subtly distinct charcoal planes, warm ivory text and restrained oxidized brass. The interface should feel like a quiet instrument panel in a stone study. Greek influence is proportion and letterform discipline; Zen influence is space, rhythm and restraint; Indian influence is limited to a subtle seal-like geometry in branding. Keep interface labels literal and useful.

Reference: Ryoku's cohesive shell and subdued dark desktop treatments; Hermes' operator orientation; Amoeba's visible sessions, ownership and progress. Do not copy artwork, wordmarks, wallpaper, layout wholesale, pricing claims, or product functionality.

## Proposed tokens

- canvas: #101211
- surface: #171A18
- raised: #1D211E
- border: #343A34
- text: #ECEAE2
- muted text: #A7AEA4
- accent: #C0A77A
- verified: #A9C2A1
- rejected: #E2A092
- inconclusive: #D6BF87
- body font: system sans-serif, no external font dependency
- evidence font: ui-monospace, SFMono-Regular, Consolas, monospace
- spacing base: 4px; common gaps 8, 12, 16, 24, 32
- panel radius: 10px; controls 6px
- motion: 140–180ms, opacity/transform only; honor reduced motion

Verify actual contrast during implementation; proposed tokens are not accessibility certification. Status always has text and icon, never color alone.

## Case workspace

A narrow left rail lists cases and their states. The main area leads with the current question, expected behavior, revision and next action. A compact horizontal stage trail shows Report / Reproduce / Repair / Verify / Review. The evidence view has Base and Candidate results side by side on desktop and stacked on mobile. Source conversation opens in a contextual drawer, with the actual Switch room link visible. A small two-person agent roster shows Fixer / Verifier, owner, active/blocked/disconnected state and last update. No ornamental graph or metric grid.

Primary views: /cases and /cases/:caseId. The initial application can open directly into a seeded case. A command palette is stretch scope.

## Interaction requirements

Keyboard focus visible; controls at least 40px tall; semantic buttons and headings. Evidence logs expand without losing scroll position. Streaming updates must not steal focus or move the action bar. A disconnected bridge gets an explicit banner and disables new requests. Last-known evidence stays readable and labelled. Mobile at 390px uses a case selector and stacked panels. Desktop check at 1440px. No glow clouds, particle backgrounds, fake terminal output, persistent pulsing, or mythological agent nicknames in controls.

## Logo handoff

User will generate a logo externally from assets/brand/LOGO-PROMPT.md and place results in assets/brand/incoming or the workspace. Inspect the actual files before adopting one. Prefer a clean SVG plus transparent PNG; preserve the original. Logo is never required to unlock development. Initial text wordmark is NYKT.
