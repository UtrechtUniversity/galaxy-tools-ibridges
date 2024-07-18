import json
import logging
import os
import signal
from flask import Flask, render_template, request
from ibridges.path import IrodsPath
from ibridges.session import Session
from ibridges.util import get_collection

log = logging.getLogger('werkzeug')
app = Flask(__name__)

debug = False
ibb = None

class iBridgesBrowser:
    """
    Class for reading iRODS/YODA paths using iBridges library
    """
    def __init__(self, 
                 irods_env_path, 
                 username,
                 password,
                 remote_path=None
                 ):
        with open(irods_env_path, 'r') as f:
            self.irods_env = json.load(f)
        self.irods_env['irods_user_name'] = username
        self.irods_env_path = irods_env_path
        self.session = Session(irods_env=self.irods_env, password=password)
        self.read_path(remote_path)

    def read_path(self, remote_path):
        # Set iRODS path to read
        self.irods_path = IrodsPath(self.session, remote_path if remote_path else '~')
        
        if not (self.irods_path.collection_exists() or self.irods_path.dataobject_exists()):
            # If the path doesn't exist, subtitute by user's root
            self.irods_path = IrodsPath(self.session, '~')
        elif self.irods_path.dataobject_exists():
            # If a object (file) rather than a collection (folder) was provided, subtitute by its folder
            self.irods_path = self.irods_path.parent

        coll = get_collection(self.session, self.irods_path)
        self.data_objects = [x.path for x in coll.data_objects]
        self.collections = [x.path for x in coll.subcollections if not x.path==str(self.irods_path)]
    
    def get_output(self):
        root = str(IrodsPath(self.session, '~'))
        path = root
        root_parts = [(path, root)]
        for part in  str(self.irods_path).split("/")[3:]:
            path = f"{path}/{part}"
            root_parts.append((path, part))

        # root_parts is for easy rendering of the breadcrumb trail
        return {
            'root': str(self.irods_path),
            'irods_env_path': self.irods_env_path,
            'root_parts': root_parts,
            'data_objects': self.data_objects,
            'collections': self.collections,
            'env': self.irods_env
            }

    def write_selected_path(self, path=None):
        # Write selected path to a file, so it can be read as the tool's output
        with open(f'/app/path', 'w') as f:
            f.write(path if path is not None else str(self.irods_path))

@app.route('/', methods=['GET'])
def root():
    path = request.args.get('path')
    if path:
        ibb.read_path(path)
    return render_template('root.html', data=ibb.get_output())

@app.route('/select', methods=['GET'])
def select():
    shutdown = request.args.get('shutdown')=='1'
    response = app.response_class(
            response=render_template('server_down.html', data={'shutdown': shutdown, 'irods_path': ibb.irods_path}),
            status=200,
            mimetype='text/html'
        )

    @response.call_on_close
    def on_close():
        if shutdown:
            ibb.write_selected_path(path='None')
        else:
            ibb.write_selected_path()
        os.kill(os.getpid(), signal.SIGINT)

    return response

if __name__ == '__main__':

    debug = os.getenv('DEBUG')=='1'
    if not debug:
        log.setLevel(logging.ERROR)
    
    ibb = iBridgesBrowser(
        irods_env_path=os.getenv('IRODS_ENV_PATH'),
        username=os.getenv('YODA_USER'),
        password=os.getenv('YODA_PASS')
    )
    ibb.write_selected_path(path='')

    app.run(host='0.0.0.0', port=5000, debug=debug)
