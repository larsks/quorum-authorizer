import os
import logging

from qexceptions import *

class QuorumBase (object):

    def __init__ (self, config, logger='quorum'):
        self.config = config
        self.log = logging.getLogger(logger)

        if not self.config.get('quorum', 'quorum directory'):
            raise ConfigurationError(
                    'Quorum directory may not be empty.')

        self.quorum_dir = os.path.join(
                self.config.get('quorum', 'quorum directory parent'),
                self.config.get('quorum', 'quorum directory'))

        if not os.path.isdir(self.quorum_dir):
            raise ConfigurationError(
                    'Quorum directory %s does not exist.' % self.quorum_dir)

    def validate(self, req):
        if not self.config.has_section('command %s' % req):
            raise ConfigurationError(
                    'Request %s does not match a configured command.' % req)


        return os.path.join(self.quorum_dir, req)

