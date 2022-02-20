# coding:utf-8
import uuid


class UUIDUtils:
    """ UUID tool class """

    @staticmethod
    def getUUID():
        """ generate UUID """
        return uuid.uuid1().hex

