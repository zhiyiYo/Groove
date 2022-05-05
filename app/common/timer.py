# coding:utf-8
from time import time


class Timer:
    """ Timer class """

    def __init__(self) -> None:
        self.__startTime = 0
        self.__endTime = 0

    def start(self):
        self.__startTime = time()*1000
        return self

    def stop(self):
        self.__endTime = time()*1000
        print(f'耗时: {(self.__endTime-self.__startTime):.0f}ms')

    def elapse(self):
        """ get elapse in milliseconds """
        return self.__endTime-self.__startTime

    def restart(self):
        """ restart timer """
        self.stop()
        self.__startTime = time()*1000
        self.__endTime = self.__startTime
        return self
