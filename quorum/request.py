import os
import stat
import pwd
import logging
import subprocess

from q_exceptions import *

class Request (object):

    def __init__ (self, path, create=False):
        if path.endswith('/'):
            path = path[:-1]

        self.path = path
        self.req_name = os.path.basename(path)

        self.log = logging.getLogger('quorum.request')

        if create:
            self.create()

        if not os.path.isdir(path):
            raise InvalidRequestError('%s is not a directory.' % path)

        self.update()

    def create(self, mode=0777):
        os.umask(0)
        os.mkdir(self.path, mode)

    def update(self):
        s = os.stat(self.path)
        self.req_uid = s.st_uid
        self.req_user = pwd.getpwuid(self.req_uid)[0]
        self.valid = True
        self.ctime = s.st_ctime

    def vote(self):
        if os.getuid() == self.req_uid:
            raise InvalidVoteError('Requestors may not vote for their own request.')

        vote = os.path.join(self.path, pwd.getpwuid(os.getuid())[0])
        open(vote, 'w').close()

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

