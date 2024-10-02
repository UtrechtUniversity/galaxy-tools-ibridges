import argparse
import json
import os
from ibridges.data_operations import download
from ibridges.path import IrodsPath
from ibridges.session import Session
from pathlib import Path
from shared import desanitize

class iBridgesDownload:

    def __init__(self, 
                 irods_env, 
                 password,
                 irods_path,
                 local_path,
                 overwrite,
                 copy_empty_folders,
                 dry_run
                 ):

        if not Path(local_path).exists():
            raise FileNotFoundError("%s does not exist" % local_path)

        session = Session(irods_env=irods_env, password=password)
        irods_path = IrodsPath(session, irods_path)
        download(
            session=session,
            irods_path=irods_path,
            local_path=local_path,
            overwrite=overwrite,
            copy_empty_folders=copy_empty_folders,
            dry_run=dry_run,
        )

if __name__=="__main__":

    argparse = argparse.ArgumentParser()
    argparse.add_argument('--irods_path', type=str, required=True)
    argparse.add_argument('--local_path', type=str, required=True)
    argparse.add_argument('--overwrite', action='store_true')
    argparse.add_argument('--copy_empty_folders', action='store_true')
    argparse.add_argument('--dry_run', action='store_true', default=False)
    args = argparse.parse_args()

    exit_code = 0

    try:

        json_string = desanitize(os.getenv('IRODS_ENV', '{}'))
        irods_env = json.loads(json_string)
        irods_env['irods_user_name'] = os.getenv('IRODS_USER', None)

        ibd = iBridgesDownload(
            irods_env=irods_env,
            password=os.getenv('IRODS_PASS', None),
            irods_path=args.irods_path,
            local_path=args.local_path,
            overwrite=args.overwrite,
            copy_empty_folders=args.copy_empty_folders,
            dry_run=args.dry_run,
        )

        with open(f'{os.environ["TOOL_DIR"]}/data_dir', 'w') as f:
            f.write(args.local_path)

    except Exception as e:
        print(str(e))
        exit_code = 1

    with open(f'{os.environ["TOOL_DIR"]}/exit_code', 'w') as f:
        f.write(str(exit_code))
            
