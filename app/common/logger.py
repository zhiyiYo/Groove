# coding:utf-8
import logging
from pathlib import Path


class Logger:
    """ 日志记录器 """

    logFolder = Path('cache/log')

    def __init__(self, fileName: str):
        """
        Parameters
        ----------
        fileName: str
            日志文件名，不包含后缀
        """
        self.logFolder.mkdir(exist_ok=True, parents=True)
        self.__logFile = self.logFolder/(fileName+'.log')
        self.__logger = logging.getLogger(fileName)
        self.__consoleHandler = logging.StreamHandler()
        self.__fileHandler = logging.FileHandler(self.__logFile, encoding='utf-8')

        # 设置日志级别
        self.__logger.setLevel(logging.DEBUG)
        self.__consoleHandler.setLevel(logging.DEBUG)
        self.__fileHandler.setLevel(logging.DEBUG)

        # 设置日志的格式
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.__consoleHandler.setFormatter(fmt)
        self.__fileHandler.setFormatter(fmt)

        self.__logger.addHandler(self.__consoleHandler)
        self.__logger.addHandler(self.__fileHandler)

    def info(self, msg):
        self.__logger.info(msg)

    def error(self, msg):
        self.__logger.error(msg)

    def debug(self, msg):
        self.__logger.debug(msg)

    def warning(self, msg):
        self.__logger.warning(msg)

    def critical(self, msg):
        self.__logger.critical(msg)
