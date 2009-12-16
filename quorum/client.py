import sys
import os
import logging
import pwd
import errno

import config
from q_exceptions import *

def check_req(cf, req):
    req = req.lower()
    if not cf.has_section('command %s' % req):
        raise ConfigurationError('Request %s does not match a configured command.' % req)

    return req

def request(cf, args):
    req = check_req(cf, args[0])

    dir = cf.get('quorum', 'request directory')
    f_req = os.path.join(dir, req)

    try:
        os.mkdir(f_req, 0777)
        logging.info('Logged a request for %s.' % req)
    except OSError, detail:
        if detail.errno == errno.EEXIST:
            raise DuplicateRequestError('A request for %s already exists.' % req)
        else:
            raise

def authorize(cf, args):
    req = check_req(cf, args[0])
    dir = cf.get('quorum', 'request directory')
    f_req = os.path.join(dir, req)

    if not os.path.isdir(f_req):
        raise NoSuchRequestError('No request for %s is pending.' % req)

    vote = os.path.join(f_req, pwd.getpwuid(os.getuid())[0])
    open(vote, 'w').close()

def parse_args():
    p = config.OptionParser()
    return p.parse_args()

def main():
    logging.basicConfig(level=logging.INFO)
    opts, args = parse_args()
    cf = config.read_config(opts)

    command = args.pop(0)

    try:
        if command == 'request':
            request(cf, args)
        elif command == 'authorize':
            authorize(cf, args)
        else:
            logging.error('Invalid command: %s' % command)
            sys.exit(1)
    except QuorumError, detail:
        logging.error('ERROR: %s' % detail)
        sys.exit(1)

if __name__ == '__main__':
	main()

