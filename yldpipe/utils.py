import logging
from common import project_dir

formatter = logging.Formatter('%(levelname)s %(lineno)d %(funcName)s %(message)s')
#formatter = logging.Formatter('%(levelname)s %(name)s %(funcName)s %(message)s')
#formatter = logging.Formatter('%(name)s %(funcName)s %(message)s')
def setup_logger(name, log_file, level=logging.DEBUG):
    """To setup as many loggers as you want"""
    if len(log_file.split('/')) == 1:
        # print("log_file given: ", log_file)
        if len(log_file.split('.')) == 3:
            log_file = log_file.split('.')
            log_file = '.'.join(log_file[1:3])
        log_file = str(project_dir.joinpath('log', log_file))
        # print("log path calc: ", log_file)
    else:
        pass
    #print("log_file: ", log_file)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def log_class_mro(cls):
    """Logs the Method Resolution Order (MRO) of a class."""
    mro = cls.__mro__
    logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)
    logger.debug("Class MRO for %s: %s", cls.__name__, ' -> '.join([c.__name__ for c in mro]))

def safe_fn(unsafe_str):
    safe = unsafe_str.replace(' ', '_')
    safe = safe.replace('/', '__')
    return safe

if __name__ == '__main__':
    from treeReorderBuilder import treeReorderBuilder
    log_class_mro(treeReorderBuilder)
