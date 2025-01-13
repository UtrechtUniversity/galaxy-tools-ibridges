import argparse
import json
import os
from ibridges.data_operations import download
from ibridges.path import IrodsPath
from ibridges.session import Session
from shared import desanitize

class iBridgesDownload:

    def __init__(self, 
                 irods_env, 
                 password,
                 irods_path,
                 separator,
                 local_path,
                 overwrite
                 ):

        session = Session(irods_env=irods_env, password=password)

        for item in irods_path.split(separator):

            # removing root slash if paths appear to be relative
            if item[:len(irods_env['irods_home'])] != irods_env['irods_home']:
                item = item.lstrip('/')

            irods_path = IrodsPath(session, item)
            download(
                session=session,
                irods_path=irods_path,
                local_path=local_path,
                overwrite=overwrite,
                copy_empty_folders=True,
                dry_run=False
            )

if __name__=="__main__":

    argparse = argparse.ArgumentParser()
    argparse.add_argument('--irods_path', type=str, required=True)
    argparse.add_argument('--local_path', type=str, required=True)
    argparse.add_argument('--overwrite', action='store_true')
    args = argparse.parse_args()

    try:
        if not os.path.exists(args.local_path):
            os.makedirs(args.local_path)

        json_string = desanitize(os.getenv('IRODS_ENV', '{}')).strip()
        irods_env = json.loads(json_string)
        irods_env['irods_user_name'] = os.getenv('IRODS_USER', None).strip()
        separator = os.getenv('SEPARATOR', '|').strip()

        iBridgesDownload(
            irods_env=irods_env,
            password=os.getenv('IRODS_PASS', None).strip(),
            irods_path=args.irods_path,
            separator=separator,
            local_path=args.local_path,
            overwrite=args.overwrite
        )

        exit(0)

    except Exception as e:
        print(str(e))
        exit(1)
