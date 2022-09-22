# coding:utf-8
import logging
import weakref
from pathlib import Path


_loggers = weakref.WeakValueDictionary()


def loggerCache(cls):
    """ decorator for caching logger """

    def wrapper(name, *args, **kwargs):
        if name not in _loggers:
            instance = cls(name, *args, **kwargs)
            _loggers[name] = instance
        else:
            instance = _loggers[name]

        return instance

    return wrapper


@loggerCache
class Logger:
    """ Logger class """

    logFolder = Path('cache/log')

    def __init__(self, fileName: str):
        """
        Parameters
        ----------
        fileName: str
            log filename which doesn't contain `.log` suffix
        """
        self.logFolder.mkdir(exist_ok=True, parents=True)
        self.__logFile = self.logFolder/(fileName+'.log')
        self.__logger = logging.getLogger(fileName)
        self.__consoleHandler = logging.StreamHandler()
        self.__fileHandler = logging.FileHandler(
            self.__logFile, encoding='utf-8')

        # set log level
        self.__logger.setLevel(logging.DEBUG)
        self.__consoleHandler.setLevel(logging.DEBUG)
        self.__fileHandler.setLevel(logging.DEBUG)

        # set log format
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.__consoleHandler.setFormatter(fmt)
        self.__fileHandler.setFormatter(fmt)

        self.__logger.addHandler(self.__consoleHandler)
        self.__logger.addHandler(self.__fileHandler)

    def info(self, msg):
        self.__logger.info(msg)

    def error(self, msg, exc_info=False):
        self.__logger.error(msg, exc_info=exc_info)

    def debug(self, msg):
        self.__logger.debug(msg)

    def warning(self, msg):
        self.__logger.warning(msg)

    def critical(self, msg):
        self.__logger.critical(msg)
