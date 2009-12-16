import logging

def setup_logging():
    qlog = logging.getLogger('quorum')
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
            '%(asctime)s: %(name)s [%(levelname)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    qlog.addHandler(handler)
    qlog.setLevel(logging.WARN)

    return qlog

