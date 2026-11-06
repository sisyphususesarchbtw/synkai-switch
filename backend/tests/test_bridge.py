import asyncio
import json

import httpx

from synkai.bridge import BridgeState, SwitchBridge


def event(sequence, *, addressed=True, command_id=None, room='room-1'):
    body = 'A coupon was applied twice.' if command_id is None else 'SYNKAI_COMMAND\n' + json.dumps({'command_id': command_id, 'action': 'repair'})
    return {'event': 'message', 'id': sequence, 'data': {'type': 'message', 'room_id': room,
        'sequence': sequence, 'payload': {'addressed': addressed, 'sender': 'operator-1',
        'sender_name': 'Aditya', 'sender_kind': 'user', 'message_id': f'message-{sequence}',
        'body': body, 'timestamp': 1793950000000, 'thread_id': None, 'attachments': []}}}


def test_unaddressed_messages_advance_cursor_without_starting_work(tmp_path):
    state = BridgeState(tmp_path / 'runtime.sqlite')
    state.accept('verifier', 'room-1', event(4, addressed=False))
    assert state.pending('verifier') == []
    assert state.session('verifier')['cursor'] == 4


def test_retried_command_with_new_event_id_is_queued_once(tmp_path):
    state = BridgeState(tmp_path / 'runtime.sqlite')
    state.accept('fixer', 'room-1', event(7, command_id='repair-001'))
    state.accept('fixer', 'room-1', event(8, command_id='repair-001'))
    assert len(state.pending('fixer')) == 1
    assert state.session('fixer')['cursor'] == 8


def test_connection_identity_and_cursor_survive_process_restart(tmp_path):
    path = tmp_path / 'runtime.sqlite'
    state = BridgeState(path)
    initial = state.session('verifier')['connection_id']
    state.accept('verifier', 'room-1', {'event': 'connection_state', 'data': {
        'generation': 3, 'rooms': ['room-1'], 'cursor': 10}})
    restored = BridgeState(path).session('verifier')
    assert restored['connection_id'] == initial
    assert restored['generation'] == 3
    assert restored['cursor'] == 10


def test_other_room_cannot_queue_work(tmp_path):
    state = BridgeState(tmp_path / 'runtime.sqlite')
    state.accept('verifier', 'room-1', event(3, room='untrusted-room'))
    assert state.pending('verifier') == []


def test_room_activity_keeps_unaddressed_messages_without_queueing_work(tmp_path):
    state=BridgeState(tmp_path/'runtime.sqlite')
    state.accept('fixer','room-1',event(1,addressed=False))
    state.accept('verifier','room-1',event(1,addressed=False))
    assert state.pending('fixer')==[]
    assert len(state.activity('room-1'))==1
    assert state.activity('room-1')[0]['actor']=='Aditya'


def test_offline_send_is_durable_and_never_marked_delivered(tmp_path):
    async def scenario():
        def offline(request):
            raise httpx.ConnectError('offline', request=request)
        state = BridgeState(tmp_path / 'runtime.sqlite')
        async with httpx.AsyncClient(transport=httpx.MockTransport(offline)) as client:
            bridge = SwitchBridge('http://localhost:8791', 'verifier', 'private-test-key', 'room-1', state, client=client)
            delivered = await bridge.send_room_action('command-1', '@fixer hello')
        assert delivered is False
        assert state.deliveries()[0]['status'] == 'pending'
    asyncio.run(scenario())


def test_registration_is_reused_after_restart(tmp_path):
    async def scenario():
        requests = []
        def server(request):
            requests.append(request)
            return httpx.Response(201, json={'id': 'agent-1', 'api_key': 'secret'})
        path = tmp_path / 'agents.json'
        async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
            first = await SwitchBridge.register_once('http://localhost:8791', 'registration', 'synkai-verifier', path, client)
            second = await SwitchBridge.register_once('http://localhost:8791', 'registration', 'synkai-verifier', path, client)
        assert first['id'] == second['id'] == 'agent-1'
        assert len(requests) == 1
    asyncio.run(scenario())


def test_outgoing_receipt_preserves_server_event_identity(tmp_path):
    async def scenario():
        state=BridgeState(tmp_path/'runtime.sqlite')
        def server(request):
            return httpx.Response(200,json={'ok':True,'event_id':'actual-switch-event'})
        async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
            bridge=SwitchBridge('http://localhost:8791','verifier','key','room',state,client=client)
            assert await bridge.send_room_action('repair-1','@fixer repair')
        assert state.deliveries()[0]['remote_id']=='actual-switch-event'
    asyncio.run(scenario())


def test_sender_and_delivery_retry_cannot_post_the_same_action_concurrently(tmp_path):
    async def scenario():
        calls=[]
        async def server(request):
            calls.append(request)
            await asyncio.sleep(.02)
            return httpx.Response(200,json={'ok':True,'event_id':'one-real-event'})
        state=BridgeState(tmp_path/'runtime.sqlite')
        async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
            bridge=SwitchBridge('http://localhost:8791','verifier','key','room',state,client=client)
            assert all(await asyncio.gather(bridge.send_room_action('same','hello'),bridge.send_room_action('same','hello')))
        assert len(calls)==1
    asyncio.run(scenario())
