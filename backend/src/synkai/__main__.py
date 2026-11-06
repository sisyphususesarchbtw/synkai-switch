import argparse
import asyncio
import json
from pathlib import Path

from .service import Runtime
from .settings import Settings
from .lease import RuntimeLease


def main():
    parser=argparse.ArgumentParser(description='Run the live Synkai Switch workflow')
    parser.add_argument('--config',type=Path,required=True,help='Private local runtime configuration')
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    data=Path(config['data_dir'])
    with RuntimeLease(data/'switch/runtime.lock'):
        runtime=Runtime(Settings.model_validate(config),data_dir=data,base_sha=config['base_sha'],
            auth_file=Path(config['auth_file']),room_url=config['room_url'],case_ref=config.get('case_ref','coupon-01'))
        asyncio.run(runtime.run())


if __name__=='__main__':
    main()
