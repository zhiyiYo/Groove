# coding:utf-8
from .dao_base import DaoBase


class AlbumInfoDao(DaoBase):
    """ 专辑信息数据库操作类 """

    table = 'tbl_album_info'
    fields = ['id', 'singer', 'album', 'year', 'genre', 'modifiedTime']

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
