# coding:utf-8
from typing import List
from .dao_base import DaoBase


class PlaylistDao(DaoBase):
    """ Playlist DAO """

    table = 'tbl_playlist'
    fields = ['name', 'singer', 'album', 'count', 'modifiedTime']

    def createTable(self):
        success = self.query.exec(f"""
            CREATE TABLE IF NOT EXISTS {self.table}(
                name TEXT PRIMARY KEY,
                singer TEXT,
                album TEXT,
                count INTEGER,
                modifiedTime INTEGER
            )
        """)
        return success


class SongPlaylistDao(DaoBase):
    """ Audio file - playlist DAO """

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

    def deleteByNameFiles(self, name:str, files: List[str]):
        """ delete bt name-file pairs """
        names = [name] * len(files)
        return self.deleteByMultiFields(name=names, file=files)
