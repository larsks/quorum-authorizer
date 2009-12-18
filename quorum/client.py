import sys
import os
import pwd
import errno
import logging

from quorumbase import QuorumBase
import qconfig
import request
import qlog
from qexceptions import *

USAGE='%prog [options] ( request | authorize ) label'

class Client (QuorumBase):

    def __init__ (self, config):
        super(Client, self).__init__(config, 'quorum.client')

    def request (self, req):
        reqdir = self.validate(req)

        try:
            req = request.Request(reqdir, create=True)
            self.log.info('Logged a request for %s.' % req)
        except OSError, detail:
            if detail.errno == errno.EEXIST:
                raise DuplicateRequestError(
                        'A request for %s already exists.' % req)
            else:
                raise

    def authorize (self, req):
        reqdir = self.validate(req)

        try:
            req = request.Request(reqdir)
            req.vote()
            self.log.info('Logged an authorization for %s.' % req)
        except OSError, detail:
            if detail.errno == errno.ENOENT:
                raise DuplicateRequestError(
                        'No request for %s exists.' % req)
            else:
                raise

def parse_args():
    p = qconfig.OptionParser(usage=USAGE)
    opts, args = p.parse_args()

    if len(args) != 2:
        p.error('Missing requirement argument(s).')

    return (opts, args)

def main():
    qlog.setup_logging()
    log = logging.getLogger('quorum.client')
    log.setLevel(logging.INFO)

    opts, args = parse_args()
    cf = qconfig.read_config(opts)
    client = Client(cf)

    command = args.pop(0)

    try:
        if command == 'request':
            client.request(args[0])
        elif command == 'authorize':
            client.authorize(args[0])
        else:
            log.error('Invalid command: %s' % command)
            sys.exit(1)
    except QuorumError, detail:
        log.error('%s' % detail)
        sys.exit(1)

if __name__ == '__main__':
	main()

