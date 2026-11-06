"""Durable human approval and bounded repair lifecycle."""
import json
import re
import sqlite3
from pathlib import Path


class WorkflowState:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS work_cases(id TEXT PRIMARY KEY, state TEXT NOT NULL)')

    def db(self):
        db = sqlite3.connect(self.path, timeout=10)
        return db

    def propose(self, case_id: str, **fields):
        record = {'id': case_id, 'status': 'NEEDS_APPROVAL', 'attempts': 0, **fields}
        with self.db() as db:
            db.execute('INSERT OR IGNORE INTO work_cases VALUES (?,?)', (case_id, json.dumps(record)))
        return self.get(case_id)

    def get(self, case_id: str):
        with self.db() as db:
            row = db.execute('SELECT state FROM work_cases WHERE id=?', (case_id,)).fetchone()
        if row is None:
            raise KeyError(case_id)
        return json.loads(row[0])

    def all(self):
        with self.db() as db:
            return [json.loads(row[0]) for row in db.execute('SELECT state FROM work_cases')]

    def recover_interrupted(self):
        for record in self.all():
            if record['status'] in {'REPAIRING','VERIFYING'}:
                self.update(record['id'],status='INCONCLUSIVE',
                    error='The previous supervisor was interrupted. Inspect the record before any explicit retry; the coding budget was retained.')

    def update(self, case_id: str, **fields):
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            record = json.loads(db.execute('SELECT state FROM work_cases WHERE id=?', (case_id,)).fetchone()[0])
            record.update(fields)
            db.execute('UPDATE work_cases SET state=? WHERE id=?', (json.dumps(record), case_id))
        return record

    def approve(self, case_id: str, event: dict, *, current_check: str) -> bool:
        payload = event.get('payload', {})
        text = re.sub(r'^\s*@[\w.-]+\s+', '', payload.get('body', '')).strip()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            record = json.loads(db.execute('SELECT state FROM work_cases WHERE id=?', (case_id,)).fetchone()[0])
            valid = (record['status'] == 'NEEDS_APPROVAL' and payload.get('addressed') is True
                and event.get('room_id') == record['room_id'] and payload.get('sender') in record['operator_ids']
                and payload.get('sender_kind') not in {'agent', 'platform'}
                and text.lower() == 'approve ' + case_id and current_check == record['check_hash'])
            if not valid:
                return False
            record.update(status='CHECK_FROZEN', approved_by=payload['sender'], approval_message_id=payload['message_id'])
            db.execute('UPDATE work_cases SET state=? WHERE id=?', (json.dumps(record), case_id))
        return True

    def reserve_attempt(self, case_id: str) -> int:
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            record = json.loads(db.execute('SELECT state FROM work_cases WHERE id=?', (case_id,)).fetchone()[0])
            if record['status'] not in {'CHECK_FROZEN', 'REJECTED', 'RETRY_APPROVED'} or record['attempts'] >= 2:
                raise ValueError('Coding attempt is already running, unapproved or exhausted')
            record.update(attempts=record['attempts']+1, status='REPAIRING')
            db.execute('UPDATE work_cases SET state=? WHERE id=?', (json.dumps(record), case_id))
        return record['attempts']

    def authorize_retry(self, case_id: str, event: dict, *, current_check: str) -> bool:
        payload=event.get('payload',{})
        text=re.sub(r'^\s*@[\w.-]+\s+','',payload.get('body','')).strip().lower()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            record=json.loads(db.execute('SELECT state FROM work_cases WHERE id=?',(case_id,)).fetchone()[0])
            valid=(record['status']=='INCONCLUSIVE' and record['attempts']<2 and record['attempts']>0
                and event.get('room_id')==record['room_id'] and payload.get('addressed') is True
                and payload.get('sender') in record['operator_ids'] and payload.get('sender_kind') not in {'agent','platform'}
                and text=='retry '+case_id and current_check==record['check_hash'])
            if not valid:
                return False
            record.update(status='RETRY_APPROVED',retry_message_id=payload['message_id'],
                previous_errors=record.get('previous_errors',[])+[record.get('error','Incomplete attempt')],error=None)
            db.execute('UPDATE work_cases SET state=? WHERE id=?',(json.dumps(record),case_id))
        return True
