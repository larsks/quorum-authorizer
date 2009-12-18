class QuorumError (Exception):
    pass

class ConfigurationError (QuorumError):
    pass

class DuplicateRequestError (QuorumError):
    pass

class NoSuchRequestError (QuorumError):
    pass

class InvalidRequestError (QuorumError):
    pass

class InvalidVoteError (QuorumError):
    pass

