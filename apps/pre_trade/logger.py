import logging
import time
import os
import pathlib
from logging.handlers import TimedRotatingFileHandler

#----------------------------------------------------------------------


def create_timed_rotating_log(path, mess_format="%(asctime)s - %(levelname)s - %(message)s"):
    """Init logging

    Arguments:
        path {string} -- absolute path to log directory

    Returns:
        logger -- logger class. Use as logger.info('message')
    """
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    log_format = mess_format
    formatter = logging.Formatter(log_format)

    handler = TimedRotatingFileHandler(path, when="d", interval=1)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def create_logger(path='../../../log-pretrade', file_log='app.log', mess_format="%(asctime)s - %(levelname)s - %(message)s"):
    """Init logging

    Arguments:
        path {[str]} -- Folder that save log, accept both abs and relative path

    Keyword Arguments:
        mess_format {str} -- [description] (default: {"%(asctime)s - %(levelname)s - %(message)s"})

    Returns:
        [logger] -- [description]
    """
    print("create_logger")
    basedir = os.path.abspath(os.path.dirname(__file__))
    # make log folder if not exist:
    log_path = os.path.abspath(os.path.join(
        basedir, path))
    pathlib.Path(log_path).mkdir(parents=True, exist_ok=True)
    # print(log_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_path = log_path + '/' + file_log
    # Setup for logger
    logger = create_timed_rotating_log(log_path, mess_format)
    logger.info('{"message":"%s"}' % ('Logger configuration completed'))
    print('logger = ',logger)
    return logger


class Logger(object):
    def __init__(self, path, file_log='app.log', mess_format="%(asctime)s - %(levelname)s - %(message)s"):
        self.log = create_logger(
            path, file_log=file_log, mess_format=mess_format)

    def message(self, *message):
        mes = ' '.join([str(m) for m in message])
        self.log.info('{"message":"%s"}' % (mes))


#----------------------------------------------------------------------
if __name__ == "__main__":
    log_file = "timed_test.log"
    print = Logger('./logs', log_file).message
    print('This is the test message', "the seconde message")
