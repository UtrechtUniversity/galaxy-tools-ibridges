import json
import logging
import os
import signal
from math import ceil
from flask import Flask, render_template, request
from ibridges.path import IrodsPath
from ibridges.session import Session
from ibridges.util import get_collection

log = logging.getLogger('werkzeug')
app = Flask(__name__)

debug = False
ibb = None
per_page = 20

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
        self.last_error = None
        self.session = None
        self.irods_path = None
        self._transport_path = transport_path
        try:
            if not password or len(password)==0:
                raise ValueError("Empty password")
            # Start iRODS session
            self.session = Session(irods_env=self.irods_env, password=password)
            # Read remote root
            self.read_path(remote_path)
            # Reset Galaxy output file
            self.write_selected_path(path='')
        except Exception as e:
            log.error(str(e))
            self.last_error = str(e)

    @property
    def transport_path(self):
        if self._transport_path and os.path.isfile(self._transport_path):
            return self._transport_path

    def readable_size(self, bytes, units=[' bytes','KB','MB','GB','TB', 'PB', 'EB']):
        """ Returns a human readable string representation of bytes """
        return str(bytes) + units[0] if bytes < 1024 else self.readable_size(bytes>>10, units[1:])

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
            # self.data_objects = [x.path for x in coll.data_objects]
            self.data_objects = [{'path': x.path,
                                  'create_time': x.create_time,
                                  'modify_time': x.modify_time,
                                  'size': self.readable_size(x.size)} for x in coll.data_objects]
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
                'last_error': self.last_error,
                'transport_path': self._transport_path }

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
            out['collections'] = self.collections
            out['data_objects'] = self.data_objects

        return out

    def write_selected_path(self, path=None):
        # File needs to exist so the reponsibility for creating it stays with
        # the Galaxy Tool, and to make sure an error can be raised so the user
        # can be made aware that the tol does not properly create the transport
        # file (= text file containing the selected iRODS path)
        if not self.transport_path:
            log.error(f"Transport path {self._transport_path!r} not a file or file does not exist")
            return

        # Write selected path to file that is read as the tool's output
        with open(self._transport_path, 'w') as f:
            f.write(path if path is not None else str(self.irods_path))

@app.route('/', methods=['GET'])
def root():
    if request.args.get('path'):
        ibb.read_path(request.args.get('path'))
    page = int(request.args.get('page', default=1))
    data = ibb.get_output()
    data['paging'] = {
        'collections': data['collections'][(page-1)*per_page:(page)*per_page],
        'data_objects': data['data_objects'][max(((page-1)*per_page)-len(data['collections']),0):((page)*per_page)-len(data['collections'])],
        'page': page,
        'per_page': per_page,
        'total_pages': ceil((len(data['collections']) + len(data['data_objects']))/per_page)
    }

    return render_template('root.html', data=data)

@app.route('/select', methods=['GET'])
def select():
    """
    Function writes the select path (if selected) to the transport file
    and shuts down the app.
    """
    path = request.args.get('path')
    shutdown = request.args.get('shutdown')=='1'
    error = None if ibb.transport_path else "Transport path not set, not a file, or file does not exist"
    response = app.response_class(
            response=render_template('server_down.html', 
                                     data={'shutdown': shutdown,
                                           'error': error,
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

    irods_env = json.loads(desanitize(os.getenv('IRODS_ENV', '{}')))
    irods_env['irods_user_name'] = os.getenv('IRODS_USER', None)
    password = os.getenv('IRODS_PASS', None)

    # When changing value of TRANSPORT_PATH make sure to change to the same 
    # value in the Galaxy tool's XML file (default: /app/path)
    ibb = iBridgesBrowser(
        irods_env=irods_env,
        password=password,
        transport_path=os.getenv('TRANSPORT_PATH','/app/path'))

    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_PORT', 5000)), debug=debug)
