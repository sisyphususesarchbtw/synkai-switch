# SYNKAI Demo Video Storyboard (2 Minutes 30 Seconds)

Target Duration: **2 minutes 30 seconds**  
Style: **Direct, observable evidence first.** No rhetorical questions or artificial drama. Calm, deep narrator cadence.

---

### Timecoded Sequence & Narration

| Timecode | Screen Display | Spoken Audio (Narration) | Visual Cues |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:20** | **The False-Green Demonstration**<br/>(Split screen: code diff + terminal) | *"This patch makes the test pass by changing the expected result from 9,000 to 8,100. The bug is still there. Ordinary CI turns green, but SYNKAI rejects it because the coding agent cannot rewrite the independent check."* | Highlight the diff weakening `assert == 9000` to `assert == 8100`. Show `pytest` green, then show Synkai marking it **REJECTED**. |
| **0:20 – 0:35** | **The Verification Boundary**<br/>(Synkai Dark Zen interface) | *"SYNKAI splits authority. The worker changing the code has zero access to the verifier's test harness. The check must fail on the original commit, pass on the candidate, and pass adjacent regressions in an isolated container."* | Pan over the obsidian UI, showing the invariant contract and stage indicators. |
| **0:35 – 1:27** | **Live Switch Room Collaboration**<br/>(Mattermost `#synkai-evidence-room`) | *"Here is our live Switch room. I report a double-coupon defect. Verifier formalizes the behavioral invariant and pauses for approval. I approve it using my linked operator account. Switch coordinates a targeted handoff to Fixer, which invokes Codex in a restricted Docker worker. Fixer proposes a source repair, and the supervisor commits candidate `87ea36f9`."* | Show report message, Verifier proposal, operator sending `@synkai-verifier approve coupon-01`, Switch handoff receipt, and candidate commit creation. |
| **1:27 – 2:05** | **Three-Stage Invariant Execution**<br/>(Dual-chamber evidence view) | *"Now Verifier tests the candidate in an isolated container with network disabled. Stage one: the frozen check fails on the original commit—8,100 versus 9,000. Stage two: the candidate passes. Stage three: zero-coupon and empty-cart regressions pass. Verification took 13.1 seconds."* | Show stage progression: Original Failed, Candidate Passed, Adjacent Passed. Show raw execution output and SHA-256 input fingerprint. |
| **2:05 – 2:30** | **Room Acceptance & Conclusion**<br/>(Mattermost & GitHub repo) | *"Evidence posts back into our Switch room. I send `@synkai-verifier accept coupon-01` to seal the decision. All 68 backend tests pass, including Docker execution. This is Stillpoint building SYNKAI for Flip the Switch: independent evidence for agentic code repairs."* | Send accept command in chat, show the final verified badge and clean GitHub repository. |

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
3. Confirm stats are visible (cumulative words dictated, WPM, fixes).
4. Upload the exported image directly in the hackathon submission form.
