# coding:utf-8
import uuid


class UUIDUtils:
    """ UUID 工具类 """

    @staticmethod
    def getUUID():
        """ 生成 UUID """
        return uuid.uuid1().hex

