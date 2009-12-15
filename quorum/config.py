import optparse
from ConfigParser import ConfigParser

DEFAULTS = {
    'config file'       : '/etc/quorum/quorum.ini',
    'valid for'         : '300',
    'user'              : 'root',
    'request directory' : '/var/lib/quorum',
        }

class OptionParser (optparse.OptionParser):

    def __init__ (self):
        optparse.OptionParser.__init__(self)
        self.add_option('-f', '--config-file',
                default=DEFAULTS['config file'],
                help='Path to configuration file.')


def read_config(opts):
    cf = ConfigParser()
    cf.read(opts.config_file)

    return cf

