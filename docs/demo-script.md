# Synkai Demo Video Storyboard (Under 3 Minutes)

The authenticated submission form requires a public or unlisted **YouTube or Loom** video under 3 minutes showing agents working in real chat. 

Target Duration: **2 minutes 30 seconds**.  
Tone: **Calm, authoritative, deliberate, deep narrator voice.** Clear pacing with no rushed cadence.

---

### Timecoded Storyboard & Spoken Lines

| Timecode | Screen Display | Narration (Spoken by Operator) | Visual Action |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:22** | **Dark Zen Synkai UI**<br/>(Full screen, obsidian void, S Y N K A I brandmark visible) | *"Every developer using AI coding agents knows the dirty secret of modern CI: your tests can turn green, and your bug is still in production. Coding agents optimize to pass checks—even if that means silently tampering with the assertions. Synkai fixes this at the root."* | Pan over the obsidian UI, showing the clean status headers and invariant checklist. |
| **0:22 – 0:45** | **Terminal & Self-Sufficient Setup**<br/>(Split or quick cut to PowerShell) | *"Everything here is self-sufficient. With one setup command, we launch Switch 0.31.0, our isolated Docker workers, and register two specialized agent identities: Synkai Fixer and Synkai Verifier."* | Show `setup-switch.ps1` starting server and registering agents cleanly. |
| **0:45 – 1:18** | **Live Mattermost Room (Switch Control Plane)**<br/>(Mattermost `#synkai-evidence-room`) | *"Here is our live Switch room. I report a double-discount defect: a 10% coupon applied twice. Verifier formalizes the invariant—10,000 cents must become 9,000—and pauses for my sovereign approval. I approve it. The check is now frozen outside the codebase."* | Show the bug report message, Verifier's proposal, and the operator sending `@synkai-verifier approve coupon-01`. |
| **1:18 – 1:42** | **Targeted Handoff & Docker Sandbox**<br/>(Mattermost & Docker worker logs) | *"Switch coordinates the targeted handoff. Fixer generates a clean Python repair using Codex in a restricted container. Notice: Fixer has zero access to the verifier's test harness. It cannot rewrite the rules or grade its own exam."* | Show targeted handoff in chat, Fixer's proposed diff, and supervisor commit. |
| **1:42 – 2:08** | **Synkai Evidence Chamber**<br/>(Return to Synkai React UI) | *"The result is absolute proof. On the base revision, the frozen check fails as expected: 8,100 versus 9,000. On the candidate patch, it passes. Zero-coupon and empty-cart regressions pass too. Verification took 13.1 seconds in an isolated, network-disabled container."* | Click into the dual-chamber view showing Base Failed, Candidate Passed, and Adjacent Checks Green. |
| **2:08 – 2:32** | **Acceptance in Chat & Wrap-up**<br/>(Mattermost & GitHub Repo) | *"The evidence card posts back into our Switch room. With one message, I accept the verified patch. This is Stillpoint building Synkai for Flip the Switch: honest agents, human sovereignty, and invariant evidence you can trust."* | Send `@synkai-verifier accept coupon-01` in chat, quick cut to GitHub repo with 68 passing tests. |

---

### Recording & Audio Checklist

1. **Resolution:** 1080p (1920x1080) at 60fps or 30fps.
2. **Audio:** High-quality microphone, clean noise floor, deep/authoritative delivery.
3. **Credentials Check:** Ensure `.env`, `auth.json`, and raw API keys are never visible on screen.
4. **Visibility:** Set video to **Unlisted** or **Public** on YouTube or Loom.
5. **Signed-Out Verification:** Test the generated link in an incognito window before submitting to confirm it plays without requiring a login.

---

### Wispr Flow Side Entry Capture

1. In Wispr Flow desktop app, navigate to: **Insights → Your usage → Share**.
2. Export the official graphic card (PNG or JPG).
3. Confirm stats are visible: ~6,756 words, 132 WPM, top 0.4%, 963 fixes.
4. Upload the exported image directly in the hackathon submission form.
