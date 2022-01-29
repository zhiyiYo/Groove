# coding:utf-8
from .dao_base import DaoBase


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