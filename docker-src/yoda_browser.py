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
    Class for reading iRODS paths using iBridges library
    """
    def __init__(self, 
                 irods_env, 
                 password,
                 remote_path=None,
                 transport_path='/app/path'
                 ):
        self.irods_env = irods_env
        self.transport_path = transport_path
        self.last_error = None
        self.session = None
        try:
            # Start iRODS session
            self.session = Session(irods_env=self.irods_env, password=password)
            # Read remote root
            self.read_path(remote_path)
            # Reset Galaxy output file
            self.write_selected_path(path='')
        except Exception as e:
            log.error(str(e))
            self.last_error = str(e)

    def read_path(self, remote_path):
        """
        Read all objects and collections in an iRODS path.
        """
        try:
            self.last_error = None

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
        except Exception as e:
            log.error(str(e))
            self.last_error = str(e)
    
    def get_output(self):

        out = { 'root': '',
                'root_parts': [],
                'data_objects': [],
                'collections': [],
                'env': self.irods_env,
                'last_error': self.last_error }

        if self.session:
            root = str(IrodsPath(self.session, '~'))
            path = root
            # root_parts allows for easy rendering of the breadcrumb trail
            root_parts = [(path, root)]
            for part in  str(self.irods_path).split("/")[3:]:
                path = f"{path}/{part}"
                root_parts.append((path, part))
            
            out['root'] = str(self.irods_path)
            out['root_parts'] = root_parts
            out['data_objects'] = self.data_objects
            out['collections'] = self.collections

        return out

    def write_selected_path(self, path=None):
        # Write selected path to file that is read as the tool's output
        with open(self.transport_path, 'w') as f:
            f.write(path if path is not None else str(self.irods_path))

@app.route('/', methods=['GET'])
def root():
    path = request.args.get('path')
    if path:
        ibb.read_path(path)
    return render_template('root.html', data=ibb.get_output())

@app.route('/select', methods=['GET'])
def select():
    """
    Function writes the select path (if selected) to the transport file
    and shuts down the app.
    """
    path = request.args.get('path')
    shutdown = request.args.get('shutdown')=='1'
    response = app.response_class(
            response=render_template('server_down.html', 
                                     data={'shutdown': shutdown,
                                           'irods_path': path if path else ibb.irods_path}),
            status=200,
            mimetype='text/html'
        )

    @response.call_on_close
    def on_close():
        if shutdown:
            ibb.write_selected_path(path='None')
        else:
            ibb.write_selected_path(path=path)
        os.kill(os.getpid(), signal.SIGINT)

    return response

def desanitize(string):
    """
    Galaxy 'sanitizes' variable when exporting them to the
    environment, this function restores the original characters.
    """
    mapped_chars = { 
        '__gt__': '>',
        '__lt__': '<',
        '__sq__': "'",
        '__dq__': '"',
        '__ob__': '[',
        '__cb__': ']',
        '__oc__': '{',
        '__cc__': '}',
        '__at__': '@',
        '__cn__': '\n',
        '__cr__': '\r',
        '__tc__': '\t',
        '__pd__': '#'}

    for key in mapped_chars.keys():
        string = string.replace(key, mapped_chars[key])

    return string


if __name__ == '__main__':

    debug = os.getenv('DEBUG')=='1'
    if not debug:
        log.setLevel(logging.ERROR)

    json_string = desanitize(os.getenv('YODA_ENV', '{}'))
    irods_env = json.loads(json_string)
    irods_env['irods_user_name'] = os.getenv('YODA_USER')

    # When changing value of TRANSPORT_PATH make sure to change to the same 
    # value in the Galaxy tool's XML file
    ibb = iBridgesBrowser(
        irods_env=irods_env,
        password=os.getenv('YODA_PASS'),
        transport_path=os.getenv('TRANSPORT_PATH','/app/path'))

    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_PORT', 5000)), debug=debug)
