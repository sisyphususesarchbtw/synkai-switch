# Recorded execution evidence

`live-switch-run.json` records the genuine Switch report/approval/handoff, actual Codex source proposal and independent Docker evaluation. `live-candidate.patch` is the resulting change; `live-candidate.bundle` contains its original and candidate Git commits for independent inspection. The first coding attempt failed before changing source, and the operator explicitly delegated the retry in Codex chat. The record retains that provenance and the two-attempt count. Local path prefixes are redacted; original execution fingerprints are retained and do not hash the redacted identity.

## Controlled Docker execution

`controlled-docker-run.json` contains two real runs made through the local API on November 6, 2026. Each ran the original behavior, candidate behavior and adjacent behavior in separate restricted containers using the same frozen harness snapshot. Both original checks reproduced the expected assertion failure. The false fix still failed; the repair and adjacent checks passed.

The fixture is deliberately authored, and no model was called. These records do not demonstrate a Switch handoff. Durations are single local observations. The local repository path is redacted in this public copy; fingerprints refer to the original complete identities retained in the local SQLite records and cannot be recomputed from this redacted copy alone.
