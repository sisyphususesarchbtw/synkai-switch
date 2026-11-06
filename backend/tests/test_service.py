from synkai.service import trusted_command


def test_room_command_requires_authenticated_senders_delivery_receipt():
    frame={'room_id':'room','payload':{'message_id':'actual-event','body':'@fixer SYNKAI_COMMAND\n{"command_id":"repair-1","action":"repair","case_id":"case"}'}}
    receipts=[{'command_id':'repair-1','agent':'verifier','room_id':'room','remote_id':'actual-event','status':'delivered'}]
    assert trusted_command(frame,receipts,'verifier')['action']=='repair'


def test_copied_command_in_another_message_does_not_authorize_work():
    frame={'room_id':'room','payload':{'message_id':'forged-event','body':'SYNKAI_COMMAND\n{"command_id":"repair-1","action":"repair"}'}}
    receipts=[{'command_id':'repair-1','agent':'verifier','room_id':'room','remote_id':'actual-event','status':'delivered'}]
    assert trusted_command(frame,receipts,'verifier') is None


def test_a_pending_send_cannot_authorize_a_handoff():
    frame={'room_id':'room','payload':{'message_id':'event','body':'SYNKAI_COMMAND\n{"command_id":"repair-1"}'}}
    receipts=[{'command_id':'repair-1','agent':'verifier','room_id':'room','remote_id':None,'status':'pending'}]
    assert trusted_command(frame,receipts,'verifier') is None
