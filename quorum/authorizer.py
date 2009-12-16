#!/usr/bin/python

import sys
import os
import time
import stat
import logging
import subprocess
import pwd

import config
import request
from q_exceptions import *

class Authorizer (object):
    def __init__ (self, config):
        self.log = logging.getLogger('quorum')
        self.config = config
        self.request_dir = self.config.get('quorum', 'request directory')
        self.valid_for = int(self.config.get('quorum', 'valid for'))

        if not os.path.isdir(self.request_dir):
            raise ConfigurationError('Request directory %s does not exist.' % self.request_dir)

    def execute(self, req):
        command = self.config.get('command %s' % req.req_name, 'command')
        user = self.config.get('command %s' % req.req_name, 'user')
        subprocess.call(['/usr/bin/sudo', '-u', user, '/bin/sh', '-c',
            command])

    def check_one_request(self, req):
        if not self.config.has_section('command %s' % req.req_name):
            self.log.error('Removing request %s: does not match a configured command.', 
                    req.req_name)
            req.delete()
            return

        if req.ctime < (time.time() - self.valid_for):
            self.log.error('Removing request %s: expired.' % req)
            req.delete()
            return

        self.log.info('Found %s.' % req)
        required_votes = int(self.config.get('command %s' % req.req_name,
            'required votes'))

        votes = req.tally()
        if votes >= required_votes:
            self.log.info('Request %s has been authorized.' % req)
            req.delete()
            self.execute(req)
        else:
            self.log.info('Request %s: have %d votes, need %d.' %
                    (req, votes, required_votes))

    def check_all_requests(self):
        self.log.info('Checking for requests.')

        for req_name in os.listdir(self.request_dir):
            req_path = os.path.join(self.request_dir, req_name)

            try:
                req = request.Request(req_path)
            except InvalidRequestError, detail:
                self.log.error('Removing request %s: invalid (%s)' % 
                        req_name, detail)
                subprocess.call(['rm', '-rf', f_req])
                continue

            self.check_one_request(req)

def parse_args():
    p = config.OptionParser()
    return p.parse_args()

def main():
    logging.basicConfig(level=logging.INFO)
    opts, args = parse_args()
    cf = config.read_config(opts)

    try:
        auth = Authorizer(cf)
        auth.check_all_requests()
    except QuorumError, detail:
        logging.error('ERROR: %s' % detail)
        sys.exit(1)

if __name__ == '__main__':
	main()

