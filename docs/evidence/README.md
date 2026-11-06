# Controlled Docker execution

`controlled-docker-run.json` contains two real runs made through the local API on November 6, 2026. Each ran the original behavior, candidate behavior and adjacent behavior in separate restricted containers using the same frozen harness snapshot. Both original checks reproduced the expected assertion failure. The false fix still failed; the repair and adjacent checks passed.

The fixture is deliberately authored, and no model was called. These records do not demonstrate a Switch handoff. Durations are single local observations. The local repository path is redacted in this public copy; fingerprints refer to the original complete identities retained in the local SQLite records and cannot be recomputed from this redacted copy alone.
