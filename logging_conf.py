import logging.config
from os import path

class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def singleton(cls):
    instances = {}
    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()

@singleton
class MyLogger():
    def __init__(self):
        logpath = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
        logging.config.fileConfig(logpath)
        self.logger = logging.getLogger('projectlogger')
        for handler in self.logger.handlers[:-1]:
            handler.addFilter(MyFilter(handler.level))