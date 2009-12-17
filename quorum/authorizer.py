#!/usr/bin/python

import sys
import os
import time
import stat
import logging
import logging.handlers
import subprocess
import pwd
import string

import config
import request
import qlog
from q_exceptions import *

global log

class Authorizer (object):
    def __init__ (self, config):
        self.log = logging.getLogger('quorum.authorizer')
        self.config = config
        self.quorum_dir = os.path.join(
                self.config.get('quorum', 'quorum directory parent'),
                self.config.get('quorum', 'quorum directory'))
        self.valid_for = int(
                self.config.get('quorum', 'valid for'))
        self.check_interval = int(
                self.config.get('quorum', 'check interval'))

        if not os.path.isdir(self.quorum_dir):
            raise ConfigurationError('Quorum directory %s does not exist.'
                % self.quorum_dir)

    def execute(self, req):
        command = self.config.get('command %s' % req.req_name, 'command')
        user = self.config.get('command %s' % req.req_name, 'user')
        subprocess.call(['/usr/bin/sudo', '-u', user, '/bin/sh', '-c',
            command])

    def check_one_request(self, req):
        if not self.config.has_section('command %s' % req.req_name):
            self.log.warn('Removing request %s: does not match a configured command.', 
                    req.req_name)
            req.delete()
            return

        if req.ctime < (time.time() - self.valid_for):
            self.log.warn('Removing request %s: expired.' % req)
            req.delete()
            return

        self.log.info('Found %s.' % req)
        required_votes = int(self.config.get('command %s' % req.req_name,
            'required votes'))

        votes = req.tally()
        if votes >= required_votes:
            self.log.warn('Request %s has been authorized.' % req)
            req.delete()
            self.execute(req)
        else:
            self.log.info('Request %s: have %d votes, need %d.' %
                    (req, votes, required_votes))

    def check_all_requests(self):
        self.log.info('Checking for requests.')

        for req_name in os.listdir(self.quorum_dir):
            req_path = os.path.join(self.quorum_dir, req_name)

            try:
                req = request.Request(req_path)
            except InvalidRequestError, detail:
                self.log.warn('Removing request %s: invalid (%s)' % 
                        req_name, detail)
                subprocess.call(['rm', '-rf', f_req])
                continue

            self.check_one_request(req)

    def loop(self):
        while True:
            loop_start = time.time()
            self.check_all_requests()
            time.sleep(self.check_interval - (time.time() - loop_start))

def parse_args():
    p = config.OptionParser()
    p.add_option('-e', '--stderr', action='store_true',
            help='Log to stderr instead of syslog.')
    p.add_option('-v', '--verbose', action='store_true',
            help='Enable more verbose logging.')
    return p.parse_args()

def main():
    global log

    log = qlog.setup_logging()
    opts, args = parse_args()

    if opts.stderr:
        log.addHandler(logging.handlers.SysLogHandler(
            address='/dev/log',
            facility=logging.handlers.SysLogHandler.LOG_DAEMON))

    if opts.verbose:
        log.setLevel(logging.INFO)

    try:
        cf = config.read_config(opts)
        auth = Authorizer(cf)
        auth.loop()
    except QuorumError, detail:
        log.error('%s' % detail)
        sys.exit(1)

if __name__ == '__main__':
	main()

