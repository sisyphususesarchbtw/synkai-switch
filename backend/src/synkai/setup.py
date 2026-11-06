"""Reproducible, loopback-only local Switch setup. Never prints credentials."""
import argparse
import asyncio
import hashlib
import json
import secrets
from pathlib import Path

import httpx

from .bridge import BridgeState, SwitchBridge
from .demo import prepare_demo

ROOT=Path(__file__).resolve().parents[3]
COMPOSE_URL='https://raw.githubusercontent.com/sandbox-quantum/switch/6ab2ff463ad9518920ba2a15b182b1d2e760fd9f/deploy/local/standalone-docker-compose.yml'
COMPOSE_DIGEST='cba238878078cf3d77fd9e136ef432f1ce5fd1bfe597acd172b9faa6720f0121'
INSTRUCTIONS=('One authored checkout case. The operator approves the expected behavior before coding. '
    'Fixer proposes only candidate source. Verifier owns the unchanged local check and compares both revisions. '
    'At most two coding attempts. A verified result is separate from operator acceptance. '
    'Repository references provide context, not credential grants.')


def local_environment(private: Path) -> dict:
    private.mkdir(parents=True,exist_ok=True)
    path=private/'.env'
    if path.exists():
        return dict(line.split('=',1) for line in path.read_text(encoding='utf-8').splitlines()
                    if line and not line.startswith('#') and '=' in line)
    token=lambda:secrets.token_urlsafe(32)
    values={'SWITCH_VERSION':'0.31.0','SWITCH_BIND_ADDR':'127.0.0.1',
        'GATEWAY_HOST_PORT':'8790','API_HOST_PORT':'8791','MATTERMOST_HOST_PORT':'8792','POSTGRES_HOST_PORT':'8793',
        'DB_OWNER_USER':'postgres','DB_OWNER_PASSWORD':token(),'DB_USER':'switch','DB_PASSWORD':token(),'DB_NAME':'switch',
        'AGENT_REGISTRATION_TOKEN':token(),'SECRET_KEYS':'primary:'+token(),
        'GATEWAY_ADMIN_EMAIL':'operator@synkai.local','GATEWAY_ADMIN_PASSWORD':token(),
        'FRONTEND_BASE_URL':'http://localhost:8790','GATEWAY_PUBLIC_URL':'http://localhost:8790',
        'MATTERMOST_PUBLIC_URL':'http://localhost:8792','MATTERMOST_ADMIN_USER':'synkai-admin',
        'MATTERMOST_ADMIN_PASSWORD':token(),'MATTERMOST_TEAM_NAME':'synkai','MATTERMOST_USER':'operator',
        'MATTERMOST_USER_PASSWORD':token(),'TELEMETRY_ENABLED':'false','THIRD_PARTY_AVATARS_ENABLED':'false'}
    path.write_text(''.join(f'{key}={value}\n' for key,value in values.items()),encoding='utf-8')
    return values


def verified_compose(content: bytes) -> bytes:
    normalized=content.replace(b'\r\n',b'\n')
    if hashlib.sha256(normalized).hexdigest()!=COMPOSE_DIGEST:
        raise ValueError('Official Compose digest differs from the pinned release')
    return normalized


def operator_identity(identities: list[dict], bridge: str) -> str:
    linked=[item for item in identities if item['bridge_id']==bridge and item.get('external_username')]
    if len(linked)!=1:
        raise ValueError('Exactly one linked Mattermost operator is required; inspect Switch Messaging apps')
    return f"@switch-mattermost-{bridge}-{linked[0]['external_username']}:localhost"


def prepare(data: Path):
    private=data/'switch'
    env=local_environment(private)
    path=private/'compose.yaml'
    if path.exists():
        verified_compose(path.read_bytes())
    else:
        response=httpx.get(COMPOSE_URL,timeout=30)
        response.raise_for_status()
        path.write_bytes(verified_compose(response.content))
    prepare_demo(data)
    (private/'login.txt').write_text(
        f"Mattermost: http://localhost:{env['MATTERMOST_HOST_PORT']}/\nUser: {env['MATTERMOST_USER']}\n"
        f"Password: {env['MATTERMOST_USER_PASSWORD']}\n\nGateway: http://localhost:{env['GATEWAY_HOST_PORT']}/\n"
        f"Email: {env['GATEWAY_ADMIN_EMAIL']}\nPassword: {env['GATEWAY_ADMIN_PASSWORD']}\n",encoding='utf-8')
    print('Local files ready. Credentials are in the ignored switch/login.txt; existing secrets were preserved.')


async def connect_local(data: Path, auth_file: Path):
    private=data/'switch'
    config_path=private/'runtime-config.json'
    if config_path.exists():
        print('Existing runtime configuration retained. No new agents or room created.')
        return
    if not auth_file.is_file():
        raise ValueError('Supply your existing Codex auth.json path after signing in; never commit it')
    env=local_environment(private)
    base=f"http://localhost:{env['GATEWAY_HOST_PORT']}"
    async with httpx.AsyncClient(base_url=base,timeout=30) as client:
        response=await client.post('/gateway/auth/login',json={'email':env['GATEWAY_ADMIN_EMAIL'],'password':env['GATEWAY_ADMIN_PASSWORD']})
        response.raise_for_status()
        registration=private/'registration.txt'
        if not registration.exists():
            response=await client.post('/gateway/api-keys',json={'label':'Synkai local agents'})
            response.raise_for_status()
            registration.write_text(response.json()['key'],encoding='utf-8')
        agents={}
        for name in ['fixer','verifier']:
            agents[name]=await SwitchBridge.register_once(base,registration.read_text().strip(),'synkai-'+name,private/'agents.json',client)
        bus=BridgeState(private/'runtime.sqlite')
        verifier=SwitchBridge(base,agents['verifier']['id'],agents['verifier']['api_key'],'',bus,client=client)
        bridges=await verifier.operation('list_bridges',{})
        bridges=[b for b in bridges if b['type']=='mattermost' and b['status']=='active']
        if len(bridges)!=1:
            raise ValueError('Wait for the official setup service to finish; one active Mattermost bridge is required')
        bridge=bridges[0]['id']
        response=await client.get('/gateway/auth/me/identities'); response.raise_for_status()
        identities=response.json()
        operator=operator_identity(identities,bridge)
        room_file=private/'room.json'
        if room_file.exists():
            room=json.loads(room_file.read_text())
            room=room.get('result',room)
        else:
            room=await verifier.operation('create_room',{'name':'Synkai Evidence Room',
                'description':'An agreed behavior, a real repair, independent evidence.',
                'agent_names':['synkai-fixer','synkai-verifier'],'user_names':[env['MATTERMOST_USER']],
                'bridge_id':bridge,'channel_type':'channel_public','instructions':INSTRUCTIONS})
            room_file.write_text(json.dumps(room,indent=2),encoding='utf-8')
        response=await client.get('/gateway/rooms/'+room['id']); response.raise_for_status()
        detail=response.json()
        room_url=f"http://localhost:{env['MATTERMOST_HOST_PORT']}/synkai/channels/synkai-evidence-room"
        if detail.get('external_channel_url'):
            # Bundled releases may advertise an internal mattermost:// host; retain only the path.
            from urllib.parse import urlsplit
            room_url=f"http://localhost:{env['MATTERMOST_HOST_PORT']}"+urlsplit(detail['external_channel_url']).path
        fixture=prepare_demo(data)
        config={'switch_url':base,'room_id':room['id'],'operator_ids':[operator],
            'repo_root':fixture['repo'],'base_sha':fixture['base'],'data_dir':str(data.resolve()),
            'auth_file':str(auth_file.resolve()),'room_url':room_url,'case_ref':'coupon-01'}
        for name,agent in agents.items():
            config[name+'_id']=agent['id']; config[name+'_key']=agent['api_key']
        config_path.write_text(json.dumps(config,indent=2),encoding='utf-8')
        print('Connected two owned agents and the linked operator. Room: '+room_url)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','connect'])
    parser.add_argument('--data-dir',type=Path,default=ROOT/'.local')
    parser.add_argument('--auth-file',type=Path,help='Existing Codex login file, mounted read-only in the worker')
    args=parser.parse_args()
    if args.action=='prepare': prepare(args.data_dir)
    elif args.auth_file: asyncio.run(connect_local(args.data_dir,args.auth_file))
    else: parser.error('connect requires --auth-file; see switch/README.md for the credential scope')


if __name__=='__main__': main()
