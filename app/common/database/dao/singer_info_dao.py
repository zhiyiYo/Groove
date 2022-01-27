# coding:utf-8
from PyQt5.QtSql import QSqlRecord

from .dao_base import DaoBase
from ..entity import SingerInfo


class SingerInfoDao(DaoBase):
    """ 歌手信息数据库操作类 """

    table = 'tbl_singer_info'
    fields = ['id', 'singer', 'genre']

    def createTable(self):
        success = self.query.exec(f"""
            CREATE TABLE IF NOT EXISTS {self.table}(
                id CHAR(32) PRIMARY KEY,
                singer TEXT,
                genre TEXT
            )
        """)
        return success

    @staticmethod
    def loadFromRecord(record: QSqlRecord) -> SingerInfo:
        singerInfo = SingerInfo()

        for i in range(record.count()):
            field = record.fieldName(i)
            singerInfo[field] = record.value(i)

        return singerInfo
