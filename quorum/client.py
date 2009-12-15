import sys
import os
import logging
import pwd

import config
import exceptions

def request(cf, args):
    dir = cf.get('quorum', 'request directory')
    req = os.path.join(dir, args[0])
    os.mkdir(req, 0777)

def authorize(cf, args):
    dir = cf.get('quorum', 'request directory')
    req = os.path.join(dir, args[0])
    vote = os.path.join(req, pwd.getpwuid(os.getuid())[0])

    open(vote, 'w').close()

def parse_args():
    p = config.OptionParser()
    return p.parse_args()

def main():
    logging.basicConfig(level=logging.INFO)
    opts, args = parse_args()
    cf = config.read_config(opts)

    command = args.pop(0)
    if command == 'request':
        request(cf, args)
    elif command == 'authorize':
        authorize(cf, args)
    else:
        logging.error('Invalid command: %s' % command)
        sys.exit(1)

if __name__ == '__main__':
	main()

