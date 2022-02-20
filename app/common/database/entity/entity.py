# coding:utf-8
from copy import deepcopy


class Entity:
    """ Entity abstract class """

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def copy(self):
        return deepcopy(self)
