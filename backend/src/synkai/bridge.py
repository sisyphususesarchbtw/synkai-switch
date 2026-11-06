"""Released Switch WebSocket/HTTP client with durable incoming work and delivery state."""
import asyncio
import json
import sqlite3
import time
from pathlib import Path
from urllib.parse import urlencode
from uuid import uuid4

import httpx
from websockets.asyncio.client import connect
from websockets.exceptions import WebSocketException


class BridgeState:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS sessions(agent TEXT PRIMARY KEY, state TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS inbox(id INTEGER PRIMARY KEY, agent TEXT NOT NULL,
                    command_id TEXT NOT NULL, event TEXT NOT NULL, status TEXT DEFAULT 'pending',
                    UNIQUE(agent, command_id));
                CREATE TABLE IF NOT EXISTS outbox(command_id TEXT PRIMARY KEY, agent TEXT NOT NULL,
                    room_id TEXT NOT NULL, content TEXT NOT NULL, status TEXT DEFAULT 'pending', error TEXT);
                CREATE TABLE IF NOT EXISTS activity(id TEXT PRIMARY KEY, room TEXT NOT NULL, payload TEXT NOT NULL);
            ''')
            if 'remote_id' not in {row[1] for row in db.execute('PRAGMA table_info(outbox)')}:
                db.execute('ALTER TABLE outbox ADD COLUMN remote_id TEXT')

    def db(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def session(self, agent: str) -> dict:
        with self.db() as db:
            initial = {'connection_id': str(uuid4()), 'cursor': None, 'generation': None,
                       'rooms': [], 'connected': False, 'last_seen': 0}
            db.execute('INSERT OR IGNORE INTO sessions VALUES (?,?)', (agent, json.dumps(initial)))
            return json.loads(db.execute('SELECT state FROM sessions WHERE agent=?', (agent,)).fetchone()[0])

    def offline(self, agent: str):
        session = self.session(agent)
        session['connected'] = False
        with self.db() as db:
            db.execute('UPDATE sessions SET state=? WHERE agent=?', (json.dumps(session), agent))

    def accept(self, agent: str, room: str, frame: dict) -> dict | None:
        session = self.session(agent)
        data, kind = frame.get('data', {}), frame.get('event')
        incoming = None
        if kind == 'connection_state':
            session.update(generation=data['generation'], rooms=data['rooms'], cursor=data['cursor'], connected=room in data['rooms'])
        if isinstance(frame.get('id'), int):
            session['cursor'] = max(frame['id'], session.get('cursor') or 0)
        session['last_seen'] = time.time()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            if kind=='message' and data.get('room_id')==room and data.get('payload',{}).get('message_id'):
                payload=data['payload']
                record={'id':payload['message_id'],'actor':payload.get('sender_name','Unknown'),
                    'body':payload.get('body','')[:8000],'timestamp':payload.get('timestamp'), 'sender':payload.get('sender')}
                db.execute('INSERT OR IGNORE INTO activity VALUES (?,?,?)',(payload['message_id'],room,json.dumps(record)))
            if kind == 'message' and data.get('room_id') == room and data.get('payload', {}).get('addressed') is True:
                payload = data['payload']
                command_id = payload['message_id']
                if 'SYNKAI_COMMAND\n' in payload['body']:
                    try:
                        command = json.loads(payload['body'].split('SYNKAI_COMMAND\n', 1)[1])
                        command_id = str(command['command_id'])
                    except (ValueError, KeyError, TypeError):
                        command_id = payload['message_id']
                changed = db.execute('INSERT OR IGNORE INTO inbox(agent,command_id,event) VALUES (?,?,?)',
                                     (agent, command_id, json.dumps(data))).rowcount
                if changed:
                    incoming = data
                else:
                    db.execute("UPDATE inbox SET event=? WHERE agent=? AND command_id=? AND status='pending'",
                               (json.dumps(data),agent,command_id))
            db.execute('UPDATE sessions SET state=? WHERE agent=?', (json.dumps(session), agent))
        return incoming

    def pending(self, agent: str) -> list[dict]:
        with self.db() as db:
            return [dict(row) | {'event': json.loads(row['event'])} for row in db.execute(
                "SELECT * FROM inbox WHERE agent=? AND status='pending' ORDER BY id", (agent,))]

    def finish(self, row_id: int):
        with self.db() as db:
            db.execute("UPDATE inbox SET status='done' WHERE id=?", (row_id,))

    def deliveries(self) -> list[dict]:
        with self.db() as db:
            return [dict(row) for row in db.execute('SELECT * FROM outbox')]

    def activity(self, room: str) -> list[dict]:
        with self.db() as db:
            rows=db.execute('SELECT payload FROM activity WHERE room=? ORDER BY rowid DESC LIMIT 40',(room,)).fetchall()
        return [json.loads(row[0]) for row in reversed(rows)]


class SwitchBridge:
    def __init__(self, base: str, agent: str, key: str, room: str, state: BridgeState,
                 *, client: httpx.AsyncClient | None = None):
        self.base, self.agent, self.key, self.room, self.state = base.rstrip('/'), agent, key, room, state
        self.client = client or httpx.AsyncClient(timeout=20)
        self._send_lock = asyncio.Lock()

    @property
    def headers(self):
        return {'Authorization': 'Bearer ' + self.key,
                'X-Switch-Connection-Id': self.state.session(self.agent)['connection_id']}

    @staticmethod
    async def register_once(base, token, name, path: Path, client: httpx.AsyncClient):
        existing = json.loads(path.read_text()) if path.exists() else {}
        if name in existing:
            return existing[name]
        response = await client.post(base.rstrip('/') + '/agents', headers={'Authorization': 'Bearer ' + token}, json={
            'name': name, 'display_name': name.replace('synkai-', '').title(),
            'description': 'Synkai behavioral verification workflow', 'connector_type': 'synkai',
            'integration_profile': {'connection_model': 'always_on', 'message_exchange': True,
                'pre_invocation_mediation': [], 'post_invocation_mediation': [], 'event_reporting': []}})
        response.raise_for_status()
        existing[name] = response.json()
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix('.pending')
        temporary.write_text(json.dumps(existing, indent=2))
        temporary.replace(path)
        return existing[name]

    async def operation(self, name: str, arguments: dict):
        response = await self.client.post(f'{self.base}/agents/{self.agent}/ops/{name}', headers=self.headers, json=arguments)
        response.raise_for_status()
        result = response.json()
        if result.get('error'):
            raise ValueError('Switch operation refused: ' + name)
        return result.get('result', result)

    async def send_room_action(self, command_id: str, content: str) -> bool:
        async with self._send_lock:
            return await self._send_room_action(command_id, content)

    async def _send_room_action(self, command_id: str, content: str) -> bool:
        with self.state.db() as db:
            db.execute('INSERT OR IGNORE INTO outbox(command_id,agent,room_id,content) VALUES (?,?,?,?)',
                       (command_id, self.agent, self.room, content))
            row = db.execute('SELECT * FROM outbox WHERE command_id=?', (command_id,)).fetchone()
            if (row['agent'], row['room_id'], row['content']) != (self.agent, self.room, content):
                raise ValueError('A command ID cannot be reused for another message')
            if row['status'] == 'delivered':
                return True
        try:
            response = await self.client.post(f'{self.base}/agents/{self.agent}/message', headers=self.headers,
                json={'room_id': self.room, 'content': content, 'metadata': {'synkai_command_id': command_id}})
            response.raise_for_status()
        except httpx.HTTPError as exc:
            with self.state.db() as db:
                db.execute('UPDATE outbox SET error=? WHERE command_id=?', (type(exc).__name__, command_id))
            return False
        with self.state.db() as db:
            db.execute("UPDATE outbox SET status='delivered',error=NULL,remote_id=? WHERE command_id=?",
                       (response.json().get('event_id'),command_id))
        return True

    def connection_url(self):
        session = self.state.session(self.agent)
        params = {'connection_id': session['connection_id'], 'rooms': self.room, 'scope': 'single',
                  'filter': 'all', 'start_from': str(session['cursor']) if session['cursor'] is not None else 'head',
                  'protocol': 8, 'protocol_accepts': 8, 'client': 'synkai', 'client_version': '0.2.0'}
        if session['generation'] is not None:
            params['expected_generation'] = session['generation']
        return self.base.replace('http', 'ws', 1) + f'/agents/{self.agent}/connection/ws?' + urlencode(params)

    async def listen(self):
        while True:
            try:
                async with connect(self.connection_url(), additional_headers={'Authorization': 'Bearer ' + self.key},
                                   max_size=1048576, open_timeout=10) as socket:
                    async for raw in socket:
                        frame = json.loads(raw)
                        if frame.get('event') in {'gap', 'refused', 'evicted'}:
                            raise RuntimeError('Switch connection needs attention: ' + frame['event'])
                        incoming = self.state.accept(self.agent, self.room, frame)
                        if frame.get('event') == 'ping':
                            await socket.send(json.dumps({'type': 'pong', 'cursor': self.state.session(self.agent)['cursor']}))
                        if incoming:
                            yield incoming
            except (OSError, WebSocketException, httpx.HTTPError):
                self.state.offline(self.agent)
                await asyncio.sleep(2)
            finally:
                self.state.offline(self.agent)
