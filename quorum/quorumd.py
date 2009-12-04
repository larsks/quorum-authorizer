import logging
import random
import string
import time

import cherrypy
from cherrypy import _cptools

class AuthenticationFailed (Exception):
    def __init__(self):
        super(AuthenticationFailed, self).__init__('Authentication failed.')

class ActiveRequest (Exception):
    def __init__(self):
        super(ActiveRequest, self).__init__('There is already an active request.')

class InvalidRequest (Exception):
    def __init__(self, rid):
        super(InvalidRequest, self).__init__('Invalid request (%s).' % rid)

def authenticated (f):
    def _(self, tok, *args, **kwargs):
        if not self.check_tok(tok):
            raise AuthenticationFailed()

        return f(self, *args, **kwargs)

    _.__name__ == f.__name__
    return _

class Quorum(_cptools.XMLRPCController):
    def __init__(self):
        self._sessions = {}
        self._auth_validity = 300
        self._request = None
        self._required_votes = 3
        self._unanimous = False

    @cherrypy.expose
    def login(self, name, password):
        tok = ''.join(random.sample(string.letters + string.digits, 16))
        self._sessions[tok] = { 'when': time.time(), 'name': name }
        return tok

    @cherrypy.expose
    @authenticated
    def request(self, command):
        print self._sessions

        if self._request:
            raise ActiveRequest()

        rid = ''.join(random.sample(string.letters + string.digits, 16))
        self._request = {
                'rid': rid,
                'votes': 0, 
                'voters': {},
                'requestor': cherrypy.request.session['name'],
                'command': command,
                }

        return rid

    @cherrypy.expose
    @authenticated
    def check(self):
        pass

    @cherrypy.expose
    @authenticated
    def respond(self, rid, response):
        if not self._request['rid'] == rid:
            raise InvalidRequest(rid)

        if response:
            if not cherrypy.request.session['name'] in self._request['voters']:
                self._request['votes'] += 1
                self._request['voters'][cherrypy.request.session['name']] = response
            else:
                pass
        elif self._unanimous:
            pass
        else:
            pass

        return True

    @cherrypy.expose
    def dump(self, what='sessions'):
        if what == 'sessions':
            return self._sessions
        elif what == 'request':
            return self._request
        else:
            return True

    @cherrypy.expose
    @authenticated
    def poll(self, rid):
        pass

    def run(self):
        cherrypy.quickstart(self, config={
            '/': {'request.dispatch': cherrypy.dispatch.XMLRPCDispatcher()},
            })

    def check_tok(self, tok):
        sess = self._sessions.get(tok)

        if not sess:
            return False
        
        if sess['when'] < time.time() - self._auth_validity:
            del self._sessions[tok]
            return False

        cherrypy.request.session = sess

        return True

def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    quorum = Quorum()
    quorum.run()

if __name__ == '__main__':
    main()

