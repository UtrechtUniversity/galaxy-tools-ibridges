from os import getenv
from json import loads

def desanitize(string):
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


def get_irods_env():
    json_string = desanitize(getenv('IRODS_ENV', '{}')).strip()
    irods_env = loads(json_string)
    irods_env['irods_user_name'] = getenv('IRODS_USER', '').strip()
    return irods_env


def fix_irods_path(irods_path, irods_home):
    # removing root slash if paths appear to be relative
    if irods_path[:len(irods_home)] != irods_home:
        irods_path = irods_path.lstrip('/')
    return irods_path

