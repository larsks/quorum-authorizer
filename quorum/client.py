import sys
import os
import pwd
import errno
import logging

import config
import request
import qlog
from q_exceptions import *

USAGE='%prog [options] ( request | authorize ) label'

global log

def check_req(cf, req):
    req = req.lower()
    if not cf.has_section('command %s' % req):
        raise ConfigurationError('Request %s does not match a configured command.' % req)

    return req

def cmd_request(cf, quorum_dir, args):
    global log
    req = check_req(cf, args[0])
    f_req = os.path.join(quorum_dir, req)

    try:
        req = request.Request(f_req, create=True)
        log.info('Logged a request for %s.' % req)
    except OSError, detail:
        if detail.errno == errno.EEXIST:
            raise DuplicateRequestError('A request for %s already exists.' % req)
        else:
            raise

def cmd_authorize(cf, quorum_dir, args):
    global log

    req = check_req(cf, args[0])
    f_req = os.path.join(quorum_dir, req)

    req = request.Request(f_req)
    req.vote()
    log.info('Logged a vote to authorize %s.' % req)

def parse_args():
    p = config.OptionParser(usage=USAGE)
    opts, args = p.parse_args()

    if len(args) != 2:
        p.error('Missing requirement argument(s).')

    return (opts, args)

def main():
    global log

    qlog.setup_logging()
    log = logging.getLogger('quorum.client')
    log.setLevel(logging.INFO)

    opts, args = parse_args()
    cf = config.read_config(opts)

    quorum_dir = os.path.join(
            cf.get('quorum', 'quorum directory parent'),
            cf.get('quorum', 'quorum directory'))

    command = args.pop(0)

    try:
        if command == 'request':
            cmd_request(cf, quorum_dir, args)
        elif command == 'authorize':
            cmd_authorize(cf, quorum_dir, args)
        else:
            log.error('Invalid command: %s' % command)
            sys.exit(1)
    except QuorumError, detail:
        log.error('ERROR: %s' % detail)
        sys.exit(1)

if __name__ == '__main__':
	main()

