import argparse
import json
import os
from ibridges.data_operations import download
from ibridges.path import IrodsPath
from ibridges.session import Session
from pathlib import Path

class iBridgesDownload:

    def __init__(self, 
                 irods_env, 
                 password,
                 remote_path,
                 local_path,
                 overwrite,
                 copy_empty_folders,
                 dry_run
                 ):
        if not Path(local_path).exists():
            raise FileNotFoundError("%s does not exist" % local_path)

        session = Session(irods_env=irods_env, password=password)
        remote_path = IrodsPath(session, remote_path)
        download(
            session=session,
            remote_path=remote_path,
            local_path=local_path,
            overwrite=overwrite,
            copy_empty_folders=copy_empty_folders,
            dry_run=dry_run,
        )

if __name__=="__main__":

    argparse = argparse.ArgumentParser()
    argparse.add_argument('--remote_path', type=str, required=True)
    argparse.add_argument('--local_path', type=str, required=True)
    argparse.add_argument('--overwrite', action='store_true')
    argparse.add_argument('--copy_empty_folders', action='store_true')
    argparse.add_argument('--dry_run', action='store_true', default=False)
    args = argparse.parse_args()

    with open(f'{os.environ["TOOL_DIR"]}/irods_environment.json', 'r') as f:
        irods_env = json.load(f)

    irods_env['irods_user_name'] = os.environ['YODA_USER']
    
    iBridgesDownload(
        irods_env=irods_env,
        password=os.environ['YODA_PASS'],
        remote_path=args.remote_path,
        local_path=args.local_path,
        overwrite=args.overwrite,
        copy_empty_folders=args.copy_empty_folders,
        dry_run=args.dry_run,
    )

    with open(f'{os.environ["TOOL_DIR"]}/data_dir', 'w') as f:
        f.write(args.local_path)
