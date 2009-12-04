import xmlrpclib

s = xmlrpclib.ServerProxy('http://localhost:8080/')

print 'creating request'
print '-' * 70
tok = s.login('lars', 'foobar')
print 'got token:', tok
print s.dump()
rid = s.request(tok, 'ls -l /etc')
print 'got rid:', rid

print
print 'voting'
print '-' * 70
for x in range(0,3):
    tok = s.login('person%d' % x, 'foobar')
    s.respond(tok, rid, True)
    print s.dump('request')

