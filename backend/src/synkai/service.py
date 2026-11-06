"""Live room supervisor. Socket readers keep heartbeats alive during slow work."""
import asyncio
import hashlib
import json
import re
import time
from pathlib import Path
from uuid import uuid4

from .bridge import BridgeState, SwitchBridge
from .coding import CodingProvider, validate_candidate
from .demo import export_snapshot
from .runner import DockerRunner, freeze_harness, harness_digest
from .settings import Settings
from .store import Store
from .verification import CheckResult, classify
from .workflow import WorkflowState

ROOT = Path(__file__).resolve().parents[3]
BEHAVIOR = 'A 10% coupon on a 10000-cent cart must leave 9000 cents. Apply the coupon exactly once.'


def trusted_command(event: dict, receipts: list[dict], expected_sender: str) -> dict | None:
    try:
        command = json.loads(event['payload']['body'].split('SYNKAI_COMMAND\n', 1)[1])
        matching = any(row['command_id'] == command['command_id'] and row['agent'] == expected_sender
            and row['room_id'] == event['room_id'] and row['status'] == 'delivered'
            and row['remote_id'] is not None and row['remote_id'] == event['payload']['message_id'] for row in receipts)
        return command if matching else None
    except (IndexError, KeyError, ValueError, TypeError):
        return None


class Runtime:
    def __init__(self, settings: Settings, *, data_dir: Path, base_sha: str, auth_file: Path,
                 room_url: str, case_ref: str = 'coupon-01'):
        if not re.fullmatch(r'[a-z0-9-]{1,64}', case_ref):
            raise ValueError('Invalid case reference')
        self.settings, self.data, self.base, self.room_url, self.case_ref = settings, data_dir, base_sha, room_url, case_ref
        self.bus = BridgeState(data_dir / 'switch/runtime.sqlite')
        self.work = WorkflowState(data_dir / 'switch/workflow.sqlite')
        self.store = Store(data_dir / 'cases.sqlite')
        for case in self.work.all():
            self.assert_case_identity(case)
        self.runner = DockerRunner()
        self.coder = CodingProvider(auth_file, data_dir / 'candidates')
        self.context_lock = asyncio.Lock()
        self.bridges = {
            'verifier': SwitchBridge(settings.switch_url, settings.verifier_id, settings.verifier_key.get_secret_value(), settings.room_id, self.bus),
            'fixer': SwitchBridge(settings.switch_url, settings.fixer_id, settings.fixer_key.get_secret_value(), settings.room_id, self.bus)}

    def assert_case_identity(self, case):
        selected=self.store.get_case(case['ui_case_id'])
        if case['base']!=self.base or selected['base']!=case['base']:
            raise ValueError('Configured base differs from the approved case; a separate approved evaluation is required')
        repository=case.get('repo_root')
        if not repository and case.get('approval_message_id'):
            # Migrate only from an immutable recorded run, never from a new configuration.
            identity=selected['runs'][-1]['evidence'].get('identity',{}) if selected['runs'] else {}
            if identity.get('base')==case['base']:
                repository=identity.get('repo')
            if not repository:
                raise ValueError('The approved repository identity is missing; inspect the original record')
        repository=repository or str(self.settings.repo_root)
        if Path(repository).resolve()!=self.settings.repo_root.resolve():
            raise ValueError('Configured repository differs from the approved case; a separate approved evaluation is required')
        if not case.get('repo_root'):
            self.work.update(case['id'],repo_root=str(Path(repository).resolve()))

    def proposal(self, event):
        existing = self.work.all()
        if existing:
            return existing[0]
        case = self.store.create_case(BEHAVIOR, self.base)
        return self.work.propose(self.case_ref, room_id=self.settings.room_id, operator_ids=self.settings.operator_ids,
            repo_root=str(self.settings.repo_root),
            base=self.base, check_hash=harness_digest(ROOT/'runner/harness'), report_id=event['payload']['message_id'],
            report=event['payload']['body'], behavior=BEHAVIOR, ui_case_id=case['id'], source_room_url=self.room_url)

    async def send(self, agent, command_id, text):
        return await self.bridges[agent].send_room_action(command_id, text)

    async def ensure_room_context(self, case):
        async with self.context_lock:
            path=self.data/'switch/context.json'
            context=json.loads(path.read_text()) if path.exists() else {}
            bridge=self.bridges['verifier']
            if not context.get('repository_reference'):
                types=await bridge.operation('list_reference_types',{})
                if not any(item['type']=='github' for item in types):
                    raise ValueError('This Switch instance does not expose the GitHub reference type')
                reference=await bridge.operation('create_reference',{'type':'github','name':'Synkai implementation',
                    'description':'Public implementation, setup and explicitly authored checkout example.',
                    'instructions':'Read the README and docs/evaluation.md. This pointer grants no repository credentials; coding uses only the locally allowlisted base snapshot.',
                    'value':{'urls':['https://github.com/sisyphususesarchbtw/synkai-switch']}})
                context['repository_reference']=reference['id']
                path.write_text(json.dumps(context,indent=2),encoding='utf-8')
            if not context.get('attached'):
                await bridge.operation('attach_reference_to_room',{'room_id':self.settings.room_id,'reference_id':context['repository_reference']})
                context['attached']=True
                path.write_text(json.dumps(context,indent=2),encoding='utf-8')
            if case.get('approval_message_id') and not context.get('document'):
                document=await bridge.operation('create_room_document',{'name':'Approved behavior: '+case['id'],
                    'description':'Verifier-authored record of the operator-approved behavior and immutable check identity.',
                    'instructions':'Consult this agreement before reviewing evidence. This room document is context; the execution boundary is the separately frozen local harness.',
                    'content':json.dumps({key:case[key] for key in ['id','behavior','base','check_hash','approval_message_id','approved_by']},indent=2)})
                context['document']=document
                path.write_text(json.dumps(context,indent=2),encoding='utf-8')
                self.work.update(case['id'],room_document=document)

    async def handoff(self, action, case, *, attempt=None):
        origin, target = ('verifier','fixer') if action == 'repair' else ('fixer','verifier')
        suffix = attempt if attempt is not None else case['attempts']
        command_id = f"{case['id']}:{action}:{suffix}"
        payload = {'command_id':command_id,'action':action,'case_id':case['id'],'base':case['base']}
        return await self.send(origin,command_id,f'@synkai-{target}\nSYNKAI_COMMAND\n'+json.dumps(payload))

    def freeze_and_reproduce(self, case):
        self.assert_case_identity(case)
        folder = self.data/'live'/case['id']
        harness = folder/'harness'
        if not harness.exists():
            freeze_harness(ROOT/'runner/harness', harness)
        if harness_digest(harness) != case['check_hash']:
            raise ValueError('The approved check changed; a new approval is required')
        original = folder/'original'
        export_snapshot(self.settings.repo_root, self.base, original)
        image = self.runner.image_identity()
        result = self.runner.run_check(original, harness, 'check.py::test_coupon_applies_once', image)
        record = {'outcome':result.outcome,'assertion':result.assertion,'collected':result.collected,'output':result.output}
        if result.outcome != 'failed' or result.assertion != 'test_coupon_applies_once':
            raise ValueError('The expected defect was not reproduced; repair is blocked')
        self.work.update(case['id'], base_result=record, runner_image=image, harness=str(harness), status='CHECK_FROZEN')

    def verify(self, case):
        self.assert_case_identity(case)
        started = time.monotonic()
        patch = case['patch']
        if self.store.get_case(case['ui_case_id'])['candidate']!=patch['candidate']:
            raise ValueError('Candidate changed before verification')
        candidate_repo = Path(patch['repo'])
        validate_candidate(candidate_repo, self.base, patch['candidate'])
        harness = Path(case['harness'])
        if harness_digest(harness) != case['check_hash']:
            raise ValueError('The frozen check changed')
        if self.runner.image_identity() != case['runner_image']:
            raise ValueError('The runner image changed after reproduction')
        run_id = uuid4().hex
        folder = self.data/'runs'/run_id
        original, candidate = folder/'original',folder/'candidate'
        export_snapshot(self.settings.repo_root,self.base,original)
        export_snapshot(candidate_repo,patch['candidate'],candidate)
        identity = {'repo':str(self.settings.repo_root),'base':self.base,'candidate':patch['candidate'],
            'harness':case['check_hash'],'image':case['runner_image'],'environment':'no-network/readonly/1cpu/512m'}
        fingerprint = hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        evidence = {'identity':identity,'base':self.base,'candidate':patch['candidate'],'image':case['runner_image'],
            'fingerprint':fingerprint,'fixture':True,'live_agents':True,'model_calls':case['attempts'],
            'coding':patch,'approval_message_id':case['approval_message_id'],'approved_by':case['approved_by'],
            'source_room_url':self.room_url,'stages':[]}
        results = []
        for label, source, selector in [('Original behavior',original,'check.py::test_coupon_applies_once'),
            ('Candidate behavior',candidate,'check.py::test_coupon_applies_once'),
            ('Adjacent behavior',candidate,'check.py::test_adjacent_zero_coupon check.py::test_adjacent_empty_cart')]:
            self.work.update(case['id'],stage=label)
            result = self.runner.run_check(source,harness,selector,case['runner_image'])
            results.append(result)
            evidence['stages'].append({'name':label,'outcome':result.outcome,'assertion':result.assertion,
                'collected':result.collected,'output':result.output})
        outcome = classify(*results,'test_coupon_applies_once')
        if harness_digest(harness) != case['check_hash']:
            outcome = 'INCONCLUSIVE'
        evidence['elapsed_ms'] = round((time.monotonic()-started)*1000)
        self.store.save_run(case['ui_case_id'],run_id,fingerprint,outcome,evidence)
        self.work.update(case['id'],status='AWAITING_REVIEW' if outcome=='VERIFIED' else outcome,
                         outcome=outcome,run_id=run_id,stage='Complete',evidence=evidence)
        return outcome

    async def handle(self, agent: str, event: dict):
        payload = event.get('payload',{})
        human = payload.get('sender') in self.settings.operator_ids and payload.get('sender_kind') not in {'agent','platform'}
        if agent == 'verifier' and human:
            cases = self.work.all()
            if not cases:
                case = self.proposal(event)
                # A proposal already delivered by this supervisor's setup is retained verbatim.
                known = any(row['command_id']=='proposal-'+case['id'] and row['status']=='delivered' for row in self.bus.deliveries())
                if not known:
                    await self.send('verifier','proposal-'+case['id'],f"Proposed behavior for {case['id']}: {BEHAVIOR} I will also check zero-percent coupons and an empty cart. This is the authored checkout example. Check: {case['check_hash'][:12]}. To approve, send @synkai-verifier approve {case['id']}.")
                return True
            case = cases[0]
            self.assert_case_identity(case)
            if self.work.authorize_retry(case['id'],event,current_check=harness_digest(ROOT/'runner/harness')):
                await self.handoff('repair',self.work.get(case['id']),attempt=case['attempts']+1)
                return True
            if self.work.approve(case['id'],event,current_check=harness_digest(ROOT/'runner/harness')):
                await self.send('verifier',case['id']+':approved',f"Approval recorded from your message. Reproducing the defect before dispatching Fixer. Case {case['id']}.")
                await asyncio.to_thread(self.freeze_and_reproduce,self.work.get(case['id']))
                case = self.work.get(case['id'])
                await self.ensure_room_context(case)
                await self.handoff('repair',case,attempt=1)
                return True
            text = re.sub(r'^\s*@[\w.-]+\s+','',payload.get('body','')).strip().lower()
            if text == 'accept '+case['id'] and case['status']=='AWAITING_REVIEW':
                current = self.store.get_case(case['ui_case_id'],{'harness':harness_digest(ROOT/'runner/harness'),
                    'image':self.runner.image_identity(),'repo':str(self.settings.repo_root),'base':self.base})
                if current['current_outcome'] != 'VERIFIED':
                    raise ValueError('Evidence changed; acceptance requires fresh verification')
                self.work.update(case['id'],status='CLOSED',accepted_by=payload['sender'],acceptance_message_id=payload['message_id'])
                await self.send('verifier',case['id']+':closed',f"Your acceptance is recorded. Case {case['id']} is closed; the patch and exact evidence remain available.")
            return True
        expected = self.settings.verifier_id if agent=='fixer' else self.settings.fixer_id
        command = trusted_command(event,self.bus.deliveries(),expected)
        if command is None:
            # A message may reach the socket before its HTTP receipt reaches the sender.
            return 'SYNKAI_COMMAND\n' not in payload.get('body','')
        case = self.work.get(command['case_id'])
        self.assert_case_identity(case)
        if command['base'] != case['base']:
            raise ValueError('Handoff base does not match the approved case')
        if agent=='fixer' and command['action']=='repair':
            attempt = self.work.reserve_attempt(case['id'])
            await self.send('fixer',case['id']+f':coding:{attempt}',f"I am creating candidate {attempt} from the approved base. The verifier's check is outside my workspace.")
            patch = await asyncio.to_thread(self.coder.propose,self.settings.repo_root,self.base,case['behavior'],
                attempt=attempt,feedback=case.get('feedback',''))
            validate_candidate(Path(patch['repo']),case['base'],patch['candidate'])
            current=self.store.get_case(case['ui_case_id'])
            self.store.set_candidate(current['id'],patch['candidate'],current['revision'])
            self.work.update(case['id'],status='CANDIDATE_READY',patch=patch)
            await self.handoff('candidate_ready',self.work.get(case['id']))
        elif agent=='verifier' and command['action']=='candidate_ready' and case['status']=='CANDIDATE_READY':
            self.work.update(case['id'],status='VERIFYING')
            await self.send('verifier',case['id']+f":verifying:{case['attempts']}",f"Candidate {case['patch']['candidate'][:12]} received. Running the unchanged check on the original, candidate and adjacent behavior.")
            outcome = await asyncio.to_thread(self.verify,case)
            case = self.work.get(case['id'])
            await self.send('verifier',case['id']+f":result:{case['attempts']}",f"{outcome}: candidate {case['patch']['candidate'][:12]}. Exact evidence: http://127.0.0.1:8787/ . This result covers the recorded checks. "+(f"Review it, then send @synkai-verifier accept {case['id']} if you accept this patch." if outcome=='VERIFIED' else 'The result does not justify acceptance.'))
            if outcome=='REJECTED' and case['attempts']<2:
                feedback=json.dumps(case['evidence']['stages'])[:4000]
                self.work.update(case['id'],feedback=feedback)
                await self.handoff('repair',self.work.get(case['id']),attempt=2)
        return True

    async def worker(self, agent):
        while True:
            for row in self.bus.pending(self.bridges[agent].agent):
                try:
                    done = await self.handle(agent,row['event'])
                except Exception as exc:
                    for case in self.work.all():
                        self.work.update(case['id'],status='INCONCLUSIVE',error=str(exc)[:350])
                    await self.send(agent,f"error:{row['id']}",'The workflow is blocked: '+str(exc)[:250]+'. No success is claimed; inspect the local evidence service.')
                    done = True
                if done:
                    self.bus.finish(row['id'])
            await asyncio.sleep(.4)

    async def reader(self, agent):
        async for _ in self.bridges[agent].listen():
            pass

    async def retry_delivery(self):
        while True:
            for row in self.bus.deliveries():
                if row['status']=='pending':
                    bridge=next((bridge for bridge in self.bridges.values() if bridge.agent==row['agent']),None)
                    if bridge:
                        await bridge.send_room_action(row['command_id'],row['content'])
            await asyncio.sleep(2)

    async def run(self):
        if any(case['status'] in {'REPAIRING','VERIFYING'} for case in self.work.all()):
            await asyncio.to_thread(self.coder.clean_orphans)
        self.work.recover_interrupted()
        tasks=[asyncio.create_task(function(agent)) for agent in self.bridges for function in (self.reader,self.worker)]
        tasks.append(asyncio.create_task(self.retry_delivery()))
        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                task.cancel()
            for bridge in self.bridges.values():
                self.bus.offline(bridge.agent)
                await bridge.client.aclose()
