"""Local durable case state. Each execution is immutable and revision-bound."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .verification import reconcile


class Conflict(ValueError):
    pass


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS cases (
                    id TEXT PRIMARY KEY, behavior TEXT NOT NULL, base TEXT NOT NULL,
                    candidate TEXT, revision INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS runs (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT UNIQUE NOT NULL,
                    case_id TEXT NOT NULL REFERENCES cases(id), fingerprint TEXT NOT NULL,
                    candidate TEXT, outcome TEXT NOT NULL, evidence TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS received (
                    room_id TEXT NOT NULL, receiver TEXT NOT NULL, command_id TEXT NOT NULL,
                    PRIMARY KEY(room_id,receiver,command_id));
            """)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys=ON")
            with conn:
                yield conn
        finally:
            conn.close()

    def create_case(self, behavior: str, base: str) -> dict:
        case_id = uuid4().hex
        with self._connect() as conn:
            conn.execute("INSERT INTO cases(id,behavior,base,created_at) VALUES (?,?,?,?)",
                         (case_id, behavior, base, datetime.now(timezone.utc).isoformat()))
        return self.get_case(case_id)

    def list_cases(self, current_inputs: dict | None = None) -> list[dict]:
        with self._connect() as conn:
            ids = [row[0] for row in conn.execute("SELECT id FROM cases ORDER BY created_at DESC")]
        return [self.get_case(case_id, current_inputs) for case_id in ids]

    def set_candidate(self, case_id: str, candidate: str, expected_revision: int) -> dict:
        with self._connect() as conn:
            changed = conn.execute("UPDATE cases SET candidate=?, revision=revision+1 WHERE id=? AND revision=?",
                                   (candidate, case_id, expected_revision)).rowcount
            if not changed:
                raise Conflict("Case changed. Reload before selecting a candidate.")
        return self.get_case(case_id)

    def save_run(self, case_id: str, run_id: str, fingerprint: str, outcome: str, evidence: dict) -> None:
        if outcome not in {"VERIFIED", "REJECTED", "INCONCLUSIVE"}:
            raise ValueError("Invalid evidence outcome")
        payload = json.dumps(evidence, sort_keys=True)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            case = conn.execute("SELECT candidate FROM cases WHERE id=?", (case_id,)).fetchone()
            if case is None:
                raise KeyError(case_id)
            existing = conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if existing:
                if (existing["case_id"], existing["fingerprint"], existing["outcome"], existing["evidence"]) != (case_id, fingerprint, outcome, payload):
                    raise Conflict("An execution ID cannot be reused for different evidence.")
                return
            conn.execute("INSERT INTO runs(id,case_id,fingerprint,candidate,outcome,evidence,created_at) VALUES (?,?,?,?,?,?,?)",
                         (run_id, case_id, fingerprint, evidence.get("candidate", case[0]), outcome,
                          payload, datetime.now(timezone.utc).isoformat()))

    def receive_once(self, room_id: str, receiver: str, command_id: str) -> bool:
        with self._connect() as conn:
            return conn.execute("INSERT OR IGNORE INTO received VALUES (?,?,?)", (room_id, receiver, command_id)).rowcount == 1

    def get_case(self, case_id: str, current_inputs: dict | None = None) -> dict:
        with self._connect() as conn:
            case = conn.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
            if case is None:
                raise KeyError(case_id)
            runs = [dict(row) for row in conn.execute("SELECT * FROM runs WHERE case_id=? ORDER BY sequence", (case_id,))]
        for run in runs:
            run["evidence"] = json.loads(run["evidence"])
        result = dict(case)
        result.update(runs=runs, current_outcome="NOT_RUN", inconsistent=False)
        if runs:
            latest = runs[-1]
            outcomes = [r["outcome"] for r in runs if r["fingerprint"] == latest["fingerprint"]]
            result["inconsistent"] = {"VERIFIED", "REJECTED"}.issubset(outcomes)
            inputs_changed = current_inputs is not None and any(
                latest["evidence"].get("identity", {}).get(key) != value or value is None
                for key, value in current_inputs.items())
            result["current_outcome"] = "STALE" if latest["candidate"] != result["candidate"] or inputs_changed else reconcile(outcomes)
        return result
