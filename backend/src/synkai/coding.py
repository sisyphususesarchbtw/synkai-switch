"""Bounded coding CLI in a container; the verifier's files are never mounted."""
import json
import ast
import re
import subprocess
import time
from pathlib import Path
from uuid import uuid4

from .demo import git
from .runner import docker_binary


def coding_command(binary: str, image: str, workspace: Path, auth_file: Path, name: str) -> list[str]:
    return [binary, 'run', '--interactive', '--rm', '--name', name, '--read-only', '--cap-drop', 'ALL',
        '--security-opt', 'no-new-privileges', '--memory', '512m', '--cpus', '1', '--pids-limit', '64',
        '--tmpfs', '/tmp:rw,nosuid,size=64m', '--tmpfs', '/home/node/.codex:rw,nosuid,uid=1000,gid=1000,size=16m',
        '--mount', f'type=bind,source={auth_file.resolve()},target=/home/node/.codex/auth.json,readonly',
        '--mount', f'type=bind,source={workspace.resolve()},target=/workspace', image,
        'exec', '--ignore-user-config', '--ignore-rules', '--ephemeral', '--json',
        '--sandbox', 'workspace-write', '-']


def validate_candidate(repo: Path, base: str, candidate: str) -> None:
    if not all(re.fullmatch(r'[a-f0-9]{40,64}', value) for value in (base, candidate)):
        raise ValueError('A full immutable commit identity is required')
    ancestor = subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', base, candidate],
                              capture_output=True, timeout=10)
    if ancestor.returncode:
        raise ValueError('Candidate must descend from the approved base')
    paths = git(repo, 'diff', '--name-only', base, candidate).splitlines()
    if not paths or set(paths) - {'cart.py', 'test_cart.py'}:
        raise ValueError('The initial supported project only allows cart.py and test_cart.py changes')
    tree = git(repo, 'ls-tree', '-r', candidate).splitlines()
    if any(not line.startswith('100644 ') or line.split('\t')[-1] not in {'cart.py', 'test_cart.py'} for line in tree):
        raise ValueError('Candidate must contain ordinary allowlisted source files only')


def apply_proposal(workspace: Path, proposal: dict) -> None:
    if set(proposal) != {'cart_py','summary'} or not isinstance(proposal['cart_py'],str) or len(proposal['cart_py'])>16384:
        raise ValueError('Invalid structured source proposal')
    try:
        ast.parse(proposal['cart_py'])
    except SyntaxError as exc:
        raise ValueError('Proposed source is invalid Python') from exc
    (workspace/'cart.py').write_text(proposal['cart_py'],encoding='utf-8')


class CodingProvider:
    def __init__(self, auth_file: Path, workspace_root: Path, binary: str | None = None):
        self.auth_file, self.workspace_root = auth_file, workspace_root
        self.binary = binary or docker_binary()

    def clean_orphans(self):
        for log in self.workspace_root.glob('*.jsonl'):
            if re.fullmatch(r'[a-f0-9]{32}',log.stem):
                subprocess.run([self.binary,'rm','-f','synkai-code-'+log.stem],capture_output=True,timeout=10)

    def propose(self, repo: Path, base: str, behavior: str, *, attempt: int = 1, feedback: str = '') -> dict:
        if attempt not in (1, 2):
            raise ValueError('Coding budget exhausted')
        if not self.auth_file.is_file():
            raise ValueError('Configure the coding provider login first')
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        job_id = uuid4().hex
        workspace = self.workspace_root / job_id
        workspace.mkdir()
        git(workspace, 'init', '-b', 'candidate')
        git(workspace, 'fetch', '--no-tags', str(repo.resolve()), base)
        git(workspace, 'checkout', '-B', 'candidate', 'FETCH_HEAD')
        git(workspace, 'config', 'user.name', 'Synkai Fixer')
        git(workspace, 'config', 'user.email', 'fixer@example.invalid')
        image = subprocess.run([self.binary, 'image', 'inspect', 'synkai-coder:local', '--format', '{{.Id}}'],
                               capture_output=True, text=True, check=True, timeout=10).stdout.strip()
        if not image.startswith('sha256:'):
            raise ValueError('Coding worker image identity unavailable')
        argv = coding_command(self.binary, image, workspace, self.auth_file, 'synkai-code-' + job_id)
        schema = {'type':'object','properties':{'cart_py':{'type':'string'},'summary':{'type':'string'}},
                  'required':['cart_py','summary'],'additionalProperties':False}
        (workspace/'.synkai-schema.json').write_text(json.dumps(schema))
        argv[-1:-1]=['--output-schema','/workspace/.synkai-schema.json']
        sources={name:(workspace/name).read_text() for name in ['cart.py','test_cart.py']}
        prompt = ('Propose a repair for this small, deliberately authored Python checkout project. '
            'The complete current source files are included below; no inspection tools are needed. '
            'Do not invoke tools, run commands, read other files or edit the workspace. Return the full replacement '
            'cart.py as cart_py and a brief summary as JSON matching the output schema. '
            'A trusted supervisor applies only cart.py, commits it and independently executes the frozen checks. '
            'Preserve the public total_after_coupon(cents, percent) function and adjacent zero-coupon/empty-cart behavior. '
            '\nHuman-approved behavior:\n'+behavior+'\nCurrent files:\n'+json.dumps(sources)+'\nFeedback:\n'+feedback)
        log = self.workspace_root / (job_id + '.jsonl')
        started = time.monotonic()
        interrupted = None
        try:
            with log.open('wb') as output:
                process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=output, stderr=subprocess.STDOUT)
                process.stdin.write(prompt.encode())
                process.stdin.close()
                while process.poll() is None:
                    if time.monotonic() - started > 180:
                        interrupted = 'Coding attempt exceeded 180 seconds'
                    elif log.stat().st_size > 262144:
                        interrupted = 'Coding output limit exceeded'
                    elif sum('"command_execution"' in line and '"item.started"' in line for line in log.read_text(errors='replace').splitlines()) > 12:
                        interrupted = 'Coding command budget exceeded'
                    if interrupted:
                        process.kill()
                        process.wait(timeout=5)
                        break
                    time.sleep(.2)
            events = []
            for line in log.read_text(errors='replace').splitlines():
                try:
                    events.append(json.loads(line))
                except ValueError:
                    continue
            completed = [event for event in events if event.get('type') == 'turn.completed']
            if interrupted or process.returncode or not completed:
                raise ValueError(interrupted or 'Coding provider did not complete. Inspect its private local log.')
            messages=[event['item']['text'] for event in events if event.get('item',{}).get('type')=='agent_message']
            if not messages:
                raise ValueError('Coding provider returned no structured source proposal')
            apply_proposal(workspace,json.loads(messages[-1]))
            git(workspace, 'add', '--', 'cart.py', 'test_cart.py')
            git(workspace, 'commit', '-m', 'fix: satisfy the human-approved coupon behavior')
            candidate = git(workspace, 'rev-parse', 'HEAD')
            validate_candidate(workspace, base, candidate)
            return {'repo': str(workspace), 'candidate': candidate, 'base': base, 'image': image,
                    'elapsed_ms': round((time.monotonic()-started)*1000), 'invocations': 1,
                    'usage': completed[-1].get('usage'), 'cost': None, 'attempt': attempt,
                    'method':'structured-source-proposal','summary':json.loads(messages[-1])['summary'],
                    'diff':git(workspace,'diff','--no-ext-diff','--no-textconv',base,candidate,'--','cart.py','test_cart.py')}
        finally:
            subprocess.run([self.binary, 'rm', '-f', 'synkai-code-' + job_id], capture_output=True, timeout=10)
