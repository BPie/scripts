""" Proxy password updater.
Usage:
    proxyupdate.py update [options] <new_password>
    proxyupdate.py add [options] (utf|url) [-f] <path>...
    proxyupdate.py remove [options] <path>

    -v, --verbose   verbose update
"""


import sys
import json
from docopt import docopt
from os.path import expanduser, exists, dirname, isfile
from os import makedirs
from urllib import quote
from collections import defaultdict


_proxyupdate_supported_enc = ['utf', 'url']

def get_app_dir():
    home = expanduser("~")
    app_name = "proxy_updater"
    conf = ".config"
    dirpath = "/".join([home, conf, app_name])

    # creating if directori does not exist
    if not exists(dirpath):
        try:
            makedirs(dirpath)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    return dirpath


def get_json_filepath():
    json_name = "files_to_update.json"
    return "/".join([get_app_dir(), json_name])

def read_paths():
    try:
        with open(get_json_filepath()) as f:
            return json.load(f)
    except:
        return None


def write_paths(new_data, force=True):
    # reading previous paths and updating with
    # new ones
    old_data = defaultdict(str, read_paths())

    # update old data with new data
    for key in new_data:
        if not force:
            filtered_paths = []
            for p in new_data[key]:
                if not isfile(p):
                    print("no such file: ", p)
                    new_data[key].remove(p)

        old_data[key] += new_data[key]

    # dumping json
    with open(get_json_filepath(), 'w') as f:
        json.dump(old_data, f)

def write_encoded_paths(new_data, encode='utf', force=True):
    if isinstance(new_data, basestring):
        new_data = [new_data]

    assert(encode in _proxyupdate_supported_enc)
    write_paths({encode: new_data}, force)


def get_saved_password():
    with read_paths() as config:
        if 'password' in config:
            return config['password']
        else:
            return None


def set_password(new_password):
    new_data = {'password': new_password}
    old_data = read_paths()

    if old_data is None:
        old_data = {}

    old_data.update(new_data)

    # dumping json
    with open(get_json_filepath(), 'w') as f:
        json.dump(old_data, f)


def get_utf_password():
    return get_saved_password()


def get_url_password():
    return quote(get_saved_password())

def get_enc_from_args(arguments):
    if arguments['url']:
        return 'url'
    elif arguments['utf']:
        return 'utf'


def main(argv):
    arguments = docopt(__doc__)

    if arguments['add']:
        data = arguments['<path>']
        enc = get_enc_from_args(arguments)
        force = arguments['-f']
        write_encoded_paths(data, enc, force)
    elif arguments['remove']:
        pass
    elif arguments['update']:
        pass

if __name__ == '__main__':
    main(sys.argv)

