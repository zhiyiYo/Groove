# coding:utf-8
from .dao_base import DaoBase


class RecentPlayDao(DaoBase):
    """ Recent play DAO """

    table = 'tbl_recent_play'
    fields = ['file', 'lastPlayedTime', 'frequency']

    def createTable(self):
        success = self.query.exec(f"""
            CREATE TABLE IF NOT EXISTS {self.table}(
                file TEXT PRIMARY KEY,
                lastPlayedTime INTEGER,
                frequency INTEGER
            )
        """)
        return success