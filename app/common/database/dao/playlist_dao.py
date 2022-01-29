# coding:utf-8
from .dao_base import DaoBase


class PlaylistDao(DaoBase):
    """ 播放列表数据库操作类 """

    table = 'tbl_playlist'
    fields = ['name', 'modifiedTime']

    def createTable(self):
        success = self.query.exec(f"""
            CREATE TABLE IF NOT EXISTS {self.table}(
                name TEXT PRIMARY KEY,
                modifiedTime INTEGER
            )
        """)
        return success


class SongPlaylistDao(DaoBase):
    """ 歌曲文件-播放列表数据库操作类 """

    table = 'tbl_song_playlist'
    fields = ['id', 'file', 'name']

    def createTable(self):
        success = self.query.exec(f"""
            CREATE TABLE IF NOT EXISTS {self.table}(
                id CHAR(32) PRIMARY KEY,
                file TEXT,
                name TEXT
            )
        """)
        return success