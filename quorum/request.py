import os
import stat
import pwd
import logging
import subprocess

from q_exceptions import *

class Request (object):

    def __init__ (self, path, log=None):
        if path.endswith('/'):
            path = path[:-1]

        self.path = path
        self.req_name = os.path.basename(path)

        self.log = log
        if self.log is None:
            self.log = logging.getLogger('quorum')

        if not os.path.isdir(path):
            raise InvalidRequestError('%s is not a directory.' % path)

        self.update()

    def update(self):
        s = os.stat(self.path)
        self.req_uid = s.st_uid
        self.req_user = pwd.getpwuid(self.req_uid)[0]
        self.valid = True
        self.ctime = s.st_ctime

    def tally(self):
        votes = set()

        if not self.valid:
            raise InvalidRequestError('This request for %s has been invalidated.' % self.req_name)

        for vote in os.listdir(self.path):
            f_vote = os.path.join(self.path, vote)
            s = os.stat(f_vote)
            if s.st_uid == self.req_uid:
                self.log.info('Ignoring vote for %s by requestor.' %
                        self.req_name)
                continue
            else:
                self.log.info('Found vote for %s by %s.' % 
                        (self.req_name, pwd.getpwuid(s.st_uid)[0]))
                votes.add(s.st_uid)

        return len(votes)

    def delete(self):
        subprocess.call(['rm', '-rf', self.path])
        self.invalidate()

    def invalidate(self):
        self.valid = False

    def __repr__ (self):
        return '<Request for %s by %s>' % (self.req_name, self.req_user)

