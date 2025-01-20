import argparse
import json
import os
from ibridges.data_operations import upload
from ibridges.path import IrodsPath
from ibridges.session import Session
from shared import desanitize, get_irods_env, fix_irods_path

class iBridgesUpload:

    def __init__(self, 
                 irods_env,
                 password):
        self.irods_env = irods_env
        self.session = Session(irods_env=irods_env, password=password)

    def check_upload_path(self, upload_path):
        if not IrodsPath(self.session, upload_path).collection_exists():
            raise NotADirectoryError(f"{irods_path!r} is not a collection (folder)")

    def upload_file(self,
                    irods_path,
                    local_path,
                    overwrite):

        irods_path = fix_irods_path(irods_path, self.irods_env['irods_home'])
        irods_path = IrodsPath(self.session, irods_path)

        upload(
            session=self.session,
            local_path=local_path,
            irods_path=irods_path,
            overwrite=overwrite,
            copy_empty_folders=True,
            dry_run=False
        )

if __name__=="__main__":

    argparse = argparse.ArgumentParser()
    argparse.add_argument('--irods_path', type=str, required=True)
    argparse.add_argument('--uploads_file', type=str, required=True)
    argparse.add_argument('--overwrite', action='store_true')
    args = argparse.parse_args()

    try:

        irods_env = get_irods_env()

        ibu = iBridgesUpload(irods_env=irods_env,
                             password=os.getenv('IRODS_PASS', None).strip())

        ibu.check_upload_path(args.irods_path)

        with open(args.uploads_file) as f:
            files = json.load(f)

        for path, name in files:
            local_path = path
            irods_path = f"{args.irods_path.strip().rstrip('/')}/{name.strip().lstrip('/')}"

            ibu.upload_file(
                irods_path=irods_path,
                local_path=local_path,
                overwrite=args.overwrite
            )

        exit(0)

    except Exception as e:
        print(str(e))
        exit(1)

