import argparse
import json
import os
from ibridges.data_operations import upload
from ibridges.path import IrodsPath
from ibridges.session import Session
from pathlib import Path
from shared import desanitize

class iBridgesUpload:

    def __init__(self, 
                 irods_env, 
                 password,
                 local_path,
                 irods_path,
                 overwrite,
                 copy_empty_folders,
                 dry_run
                 ):

        if not Path(local_path).exists():
            raise FileNotFoundError("%s does not exist" % local_path)

        session = Session(irods_env=irods_env, password=password)
        irods_path = IrodsPath(session, irods_path)
        upload(
            session=session,
            local_path=local_path,
            irods_path=irods_path,
            overwrite=overwrite,
            copy_empty_folders=copy_empty_folders,
            dry_run=dry_run,
        )

if __name__=="__main__":

    argparse = argparse.ArgumentParser()
    argparse.add_argument('--local_path', type=str, required=True)
    argparse.add_argument('--irods_path', type=str, required=True)
    argparse.add_argument('--overwrite', action='store_true')
    argparse.add_argument('--copy_empty_folders', action='store_true')
    argparse.add_argument('--dry_run', action='store_true', default=False)
    args = argparse.parse_args()

    exit_code = 0

    try:

        json_string = desanitize(os.getenv('YODA_ENV', '{}'))
        irods_env = json.loads(json_string)
        irods_env['irods_user_name'] = os.getenv('YODA_USER', None)

        iBridgesUpload(
            irods_env=irods_env,
            password=os.getenv('YODA_PASS', None),
            local_path=args.local_path,
            irods_path=args.irods_path,
            overwrite=args.overwrite,
            copy_empty_folders=args.copy_empty_folders,
            dry_run=args.dry_run,
        )
    
    except Exception as e:
        print(str(e))
        exit_code = 1

    with open(f'{os.environ["TOOL_DIR"]}/exit_code', 'w') as f:
        f.write(str(exit_code))
