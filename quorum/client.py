import sys
import os
import logging
import pwd
import errno

import config
import request
from q_exceptions import *

USAGE='%prog [options] ( request | authorize ) label'

def check_req(cf, req):
    req = req.lower()
    if not cf.has_section('command %s' % req):
        raise ConfigurationError('Request %s does not match a configured command.' % req)

    return req

def cmd_request(cf, args):
    req = check_req(cf, args[0])

    dir = cf.get('quorum', 'request directory')
    f_req = os.path.join(dir, req)

    try:
        req = request.Request(f_req, create=True)
        logging.info('Logged a request for %s.' % req)
    except OSError, detail:
        if detail.errno == errno.EEXIST:
            raise DuplicateRequestError('A request for %s already exists.' % req)
        else:
            raise

def cmd_authorize(cf, args):
    req = check_req(cf, args[0])
    dir = cf.get('quorum', 'request directory')
    f_req = os.path.join(dir, req)

    req = request.Request(f_req)
    req.vote()
    logging.info('Logged a vote to authorize %s.' % req)

def parse_args():
    p = config.OptionParser(usage=USAGE)
    opts, args = p.parse_args()

    if len(args) != 2:
        p.error('Missing requirement argument(s).')

    return (opts, args)

def main():
    logging.basicConfig(level=logging.INFO)
    opts, args = parse_args()
    cf = config.read_config(opts)

    command = args.pop(0)

    try:
        if command == 'request':
            cmd_request(cf, args)
        elif command == 'authorize':
            cmd_authorize(cf, args)
        else:
            logging.error('Invalid command: %s' % command)
            sys.exit(1)
    except QuorumError, detail:
        logging.error('ERROR: %s' % detail)
        sys.exit(1)

if __name__ == '__main__':
	main()

