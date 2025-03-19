import argparse
import json
import os
from ibridges.data_operations import download
from ibridges.path import IrodsPath
from ibridges.session import Session
from shared import desanitize, get_irods_env, fix_irods_path

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
            irods_path = fix_irods_path(item, irods_env['irods_home'])
            irods_path = IrodsPath(session, irods_path)

            if irods_path.dataobject_exists():
                download(
                    session=session,
                    irods_path=irods_path,
                    local_path=local_path,
                    overwrite=overwrite,
                    copy_empty_folders=False,
                    dry_run=False
                )
            elif irods_path.collection_exists():
                for coll_or_obj in irods_path.walk(depth=1):
                    if coll_or_obj.dataobject_exists():
                        download(
                            session=session,
                            irods_path=coll_or_obj,
                            local_path=local_path,
                            overwrite=overwrite,
                            copy_empty_folders=False,
                            dry_run=False
                        )
            else:
                print(f"Skipped {item!r}: not a dataobject or collection")


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--irods_path', type=str, required=True)
    parser.add_argument('--local_path', type=str, required=True)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    try:
        password = os.getenv('IRODS_PASS', None)

        if not password or len(password)==0:
            raise ValueError("Empty password")

        if not os.path.exists(args.local_path):
            os.makedirs(args.local_path)

        irods_env = get_irods_env()
        separator = os.getenv('SEPARATOR', '|').strip()

        iBridgesDownload(
            irods_env=irods_env,
            password=password,
            irods_path=args.irods_path,
            separator=separator,
            local_path=args.local_path,
            overwrite=args.overwrite
        )

        exit(0)

    except Exception as e:
        print(str(e))
        exit(1)
