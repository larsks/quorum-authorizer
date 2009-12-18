import sys
import os
import optparse
from ConfigParser import ConfigParser

from qexceptions import *

DEFAULTS = {
    'config file'       : os.environ.get('QUORUM_CONFIG',
        '/etc/quorum/quorum.ini'),
    'valid for'         : '300',
    'user'              : 'root',
    'quorum directory parent'  : '/var/lib/',
    'quorum directory' : 'quorum',
    'required votes'    : '2',
    'check interval'    : '10',
        }

class OptionParser (optparse.OptionParser):

    def __init__ (self, *args, **kwargs):
        optparse.OptionParser.__init__(self, *args, **kwargs)
        self.add_option('-f', '--config-file',
                default=DEFAULTS['config file'],
                help='Path to configuration file.')

def read_config(opts):
    cf = ConfigParser(defaults=DEFAULTS)
    cf.read(opts.config_file)

    if not cf.has_section('quorum'):
        raise ConfigurationError('Configuration file is missing or invalid.')

    return cf

