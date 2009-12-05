import sys
import logging
import asyncore
import asynchat
import socket
import random
import string

STATE_INITIAL   = 0
STATE_AUTH      = 1
STATE_NEWREQ    = 2
STATE_GETREQ    = 3
STATE_VOTED     = 4

class QuorumException(Exception):
    pass

class AuthenticationFailed(QuorumException):
    def __init__(self):
        super(AuthenticationFailed, self).__init__(
                'Authentication failed.')
class PendingRequest(QuorumException):
    def __init__(self):
        super(PendingRequest, self).__init__(
                'There is already a pending request.')
class InvalidRequest(QuorumException):
    def __init__(self):
        super(InvalidRequest, self).__init__(
                'Invalid request.')
class NotImplemented(QuorumException):
    def __init__(self):
        super(NotImplemented, self).__init__(
                'That command is not implemented.')
class DuplicateVote(QuorumException):
    def __init__(self):
        super(DuplicateVote, self).__init__(
                'You have already voted.')
class NoVoteForYou(QuorumException):
    def __init__(self):
        super(NoVoteForYou, self).__init__(
                'You may not vote on your own request.')
class InvalidCommand(QuorumException):
    def __init__(self):
        super(InvalidCommand, self).__init__(
                'That command is not valid at this time.')

def authenticated(f):
    def _(self, *args, **kwargs):
        if not self.authenticated:
            self.server.log.error('%s called by unauthenticated client.' \
                    % f.__name__)
            raise AuthenticationFailed()

        return f(self, *args, **kwargs)

    return _

class QuorumChannel(asynchat.async_chat):
    def __init__(self, server, sock, addr):
        asynchat.async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator("\r\n")
        self.data = []
        self.authenticated = False

        self.state = 0
        self.states = {
                STATE_INITIAL   : ('AUTH', 'QUIT'),
                STATE_AUTH      : ('QUIT', 'NEWREQ', 'GETREQ'),
                STATE_GETREQ    : ('QUIT', 'VOTE'),
                STATE_NEWREQ    : ('QUIT'),
                STATE_VOTED     : ('QUIT'),
                }

    def collect_incoming_data(self, data):
        self.data.append(data)

    def found_terminator(self):
        try:
            command, args = ''.join(self.data).split(None, 1)
            args = args.split()
        except:
            command = ''.join(self.data)
            args = []
        command = command.upper()
        self.data = []

        try:
            self.server.log.info('Command: %s (%s).' \
                    % (command, ','.join(args)))

            if command in self.states[self.state]:
                if hasattr(self, 'handle_%s' % command):
                    getattr(self, 'handle_%s' % command)(*args)
                else:
                    raise NotImplemented()
            else:
                raise InvalidCommand()
        except QuorumException, detail:
            self.err(str(detail))
        except Exception, detail:
            self.err(str(detail))
            self.close_when_done()
            self.shutdown = True

    def okay(self, msg='Okay.'):
        self.push('OK %s\r\n' % msg)

    def err(self, msg='Error.'):
        self.push('ERR %s\r\n' % msg)

    def handle_AUTH(self, name, password):
        if self.server.authenticate(name, password):
            self.authenticated = True
            self.name = name.lower()
            self.state = STATE_AUTH
            self.okay('Authenticated.')
        else:
            raise AuthenticationFailed()

    @authenticated
    def handle_NEWREQ(self, label):
        self.server.newreq(self, label)
        self.state = STATE_NEWREQ
        self.okay('Your request has been posted.')

    @authenticated
    def handle_GETREQ(self):
        req = self.server.getreq()
        print 'REQ:', req
        if req:
            self.state = STATE_GETREQ
            self.push('* %(id)s %(requestor)s %(label)s\r\n' % \
                    self.server.request)
        self.okay()

    @authenticated
    def handle_VOTE(self, reqid, response):
        self.server.register_response(reqid, self, response)
        self.okay('Your vote has been received.')
        self.state = STATE_VOTED

    def handle_QUIT(self):
        self.okay('Quitting.')
        self.close_when_done()

class QuorumServer(asyncore.dispatcher):

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        
        self.log = logging.getLogger('QuorumServer')
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(('', 9000))
        self.listen(5)

        self.request = None

    def handle_accept(self):
        conn, addr = self.accept()
        self.log.info('Accepted connection from %s.' % str(addr))
        QuorumChannel(self, conn, addr)

    def loop(self):
        self.log.info('Starting loop.')
        asyncore.loop()

    def authenticate(self, user, password):
        return True

    def getreq(self):
        return self.request

    def newreq(self, requestor, label):
        if self.request:
            raise PendingRequest()

        self.request = {
                'id': self.get_request_id(),
                'requestor': requestor.name,
                'label': label,
                'required_votes': 3,
                'votes': {},
                'unanimous': False,
                }
        self.log.info('New request: %(label)s from %(requestor)s.' \
                % self.request)

    def get_request_id(self):
        return ''.join(random.sample(\
                string.letters + string.digits, 16))

    def register_response(self, reqid, responder, response):
        if not self.request or not reqid == self.request['id']:
            raise InvalidRequest()

        if responder.name == self.request['requestor']:
            raise NoVoteForYou()
        if responder.name in self.request['votes']:
            raise DuplicateVote()

        self.request['votes'][responder.name] = (
                int(response), responder)

        self.tally()

    def tally(self):
        yesvotes = 0
        novotes = 0
        for k, v in self.request['votes'].items():
            if v[0]:
                yesvotes += 1
            else:
                novotes += 1
        
        self.log.info('Request %s: %d for, %d against.' \
                % (self.request['id'], yesvotes, novotes))

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    s = QuorumServer()
    s.loop()

