#!/usr/bin/python

import sys
import os
import time
import stat
import logging
import subprocess
import pwd

import config
from exceptions import *

class Authorizer (object):
    def __init__ (self, config):
        if not config.has_section('quorum'):
            raise ConfigurationError('Configuration file is missing or invalid.')

        self.log = logging.getLogger('quorum')
        self.config = config
        self.request_dir = self.config.get('quorum', 'request directory')
        self.valid_for = int(self.config.get('quorum', 'valid for'))

        if not os.path.isdir(self.request_dir):
            raise ConfigurationError('Request directory does not exist.')

    def execute(self, req):
        command = self.config.get('command %s' % req, 'command')
        user = self.config.get('command %s' % req, 'user')
        subprocess.call(['/usr/bin/sudo', '-u', user] + command.split())

    def check_one_request(self, req, f_req):
        s = os.stat(f_req)
        requestor = pwd.getpwuid(s.st_uid)[0]
        self.log.info('Found request %s by %s.' % (req, requestor))
        votes = set()
        required_votes = int(self.config.get('command %s' % req,
            'required votes'))

        for vote in os.listdir(f_req):
            voter = pwd.getpwuid(os.stat(os.path.join(f_req,
                vote)).st_uid)[0]

            if voter == requestor:
                self.log.error('Ignoring vote for %s by requestor (%s)' %
                        (req, voter))
            else:
                votes.add(voter)


        if len(votes) == required_votes:
            self.log.info('Request %s by %s has been authorized.' %
                    (req, requestor))
            subprocess.call(['rm', '-rf', f_req])
            self.execute(req)
        else:
            self.log.info('Have %d votes, need %d.' %
                    (len(votes), required_votes))

    def check_all_requests(self):
        self.log.info('Checking for requests.')

        for req in os.listdir(self.request_dir):
            f_req = os.path.join(self.request_dir, req)
            if not os.path.isdir(f_req):
                self.log.error('Removing bogus item %s.' % f_req)
                subprocess.call(['rm', '-f', f_req])
                continue
            
            if not self.config.has_section('command %s' % req):
                self.log.error('Removing request %s: does not match a configured command.', req)
                subprocess.call(['rm', '-rf', f_req])
                continue

            s = os.stat(f_req)
            if s.st_ctime < (time.time() - self.valid_for):
                self.log.error('Removing request %s: expired.' % req)
                subprocess.call(['rm', '-rf', f_req])
                continue

            self.check_one_request(req, f_req)

def parse_args():
    p = config.OptionParser()
    return p.parse_args()

def main():
    logging.basicConfig(level=logging.INFO)
    opts, args = parse_args()
    cf = config.read_config(opts)

    auth = Authorizer(cf)
    auth.check_all_requests()

if __name__ == '__main__':
	main()

