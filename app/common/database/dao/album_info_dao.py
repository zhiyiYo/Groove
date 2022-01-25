# coding:utf-8
from PyQt5.QtSql import QSqlRecord

from .dao_base import DaoBase
from ..entity.album_info import AlbumInfo


class AlbumInfoDao(DaoBase):
    """ 专辑信息数据库操作类 """

    table = 'tbl_album_info'
    fields = ['id', 'singer', 'album', 'year', 'genre', 'modifiedTime']

    def __init__(self):
        super().__init__()

    def createTable(self):
        success = self.query.exec(f"""
            CREATE TABLE IF NOT EXISTS {self.table}(
                id CHAR(32) PRIMARY KEY,
                singer TEXT,
                album TEXT,
                year YEAR,
                genre TEXT,
                modifiedTime INTEGER
            )
        """)
        return success

    @staticmethod
    def loadFromRecord(record: QSqlRecord) -> AlbumInfo:
        albumInfo = AlbumInfo()

        for i in range(record.count()):
            field = record.fieldName(i)
            albumInfo[field] = record.value(i)

        return albumInfo
