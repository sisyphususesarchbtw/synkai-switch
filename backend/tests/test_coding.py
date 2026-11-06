from pathlib import Path

import pytest

from synkai.coding import coding_command, validate_candidate, apply_proposal
from synkai.demo import git, prepare_demo


def test_coder_can_write_only_candidate_and_cannot_write_host_auth(tmp_path):
    argv = coding_command('docker', 'sha256:worker', tmp_path / 'candidate', tmp_path / 'auth.json', 'case-1')
    assert '--privileged' not in argv
    assert '--read-only' in argv
    assert '--cap-drop' in argv and 'ALL' in argv
    mounts = [argv[i + 1] for i, value in enumerate(argv) if value == '--mount']
    assert len(mounts) == 2
    assert any('target=/home/node/.codex/auth.json,readonly' in mount for mount in mounts)
    assert any('target=/workspace' in mount for mount in mounts)
    assert not any('docker.sock' in mount or '/harness' in mount for mount in mounts)
    assert argv[argv.index('--sandbox') + 1] == 'workspace-write'


def test_coding_prompt_reaches_container_stdin(tmp_path):
    argv = coding_command('docker', 'sha256:worker', tmp_path, tmp_path / 'auth.json', 'case-1')
    assert '--interactive' in argv


def test_candidate_must_descend_from_frozen_base(tmp_path):
    fixture = prepare_demo(tmp_path / 'fixture')
    repo = Path(fixture['repo'])
    validate_candidate(repo, fixture['base'], fixture['candidates']['real-fix'])
    with pytest.raises(ValueError):
        validate_candidate(repo, fixture['candidates']['real-fix'], fixture['base'])


def test_only_supported_source_files_can_enter_a_candidate(tmp_path):
    fixture = prepare_demo(tmp_path / 'fixture')
    repo = Path(fixture['repo'])
    (repo / 'conftest.py').write_text('raise RuntimeError("do not load")')
    git(repo, 'add', 'conftest.py')
    git(repo, 'commit', '-m', 'attempt to change test loading')
    with pytest.raises(ValueError):
        validate_candidate(repo, fixture['base'], git(repo, 'rev-parse', 'HEAD'))


def test_structured_proposal_only_changes_the_allowed_source(tmp_path):
    (tmp_path/'cart.py').write_text('original')
    (tmp_path/'test_cart.py').write_text('human test stays unchanged')
    source='def total_after_coupon(cents, percent):\n    return cents * (100-percent) // 100\n'
    apply_proposal(tmp_path,{'cart_py':source,'summary':'Apply coupon once'})
    assert (tmp_path/'cart.py').read_text()==source
    assert (tmp_path/'test_cart.py').read_text()=='human test stays unchanged'


def test_proposal_cannot_choose_a_path_or_write_invalid_python(tmp_path):
    with pytest.raises(ValueError):
        apply_proposal(tmp_path,{'cart_py':'invalid syntax !!','summary':'bad'})
    with pytest.raises(ValueError):
        apply_proposal(tmp_path,{'cart_py':'x=1','summary':'bad','path':'../private'})
    assert list(tmp_path.iterdir())==[]
