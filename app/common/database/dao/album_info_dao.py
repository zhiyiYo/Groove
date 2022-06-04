# coding:utf-8
from typing import List

from ..entity import AlbumInfo
from .dao_base import DaoBase, finishQuery


class AlbumInfoDao(DaoBase):
    """ Album information DAO """

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

    def listBySingerAlbums(self, singers: List[str], albums: List[str]) -> List[AlbumInfo]:
        """ list album information by singer names and album names """
        if len(singers) != len(albums):
            raise ValueError('歌手和专辑列表的长度必须相同')

        values = []
        orders = []
        for i, (singer, album) in enumerate(zip(singers, albums), 1):
            value = f"('{self.adjustText(singer)}', '{self.adjustText(album)}')"
            values.append(value)
            orders.append(f'WHEN {value} THEN {i}')

        sql = f"""SELECT * FROM {self.table} WHERE (singer, album) in (VALUES
                    {','.join(values)}
                )
                ORDER BY
                    CASE (singer, album)
                    {' '.join(orders)}
                    END
            """
        if not self.query.exec(sql):
            return []

        return self.iterRecords()

    @finishQuery
    def deleteBySingerAlbums(self, singers: List[str], albums: List[str]):
        """ remove album information by singer names and album names """
        if len(singers) != len(albums):
            raise ValueError('歌手和专辑列表的长度必须相同')

        values = []
        for singer, album in zip(singers, albums):
            value = f"('{self.adjustText(singer)}', '{self.adjustText(album)}')"
            values.append(value)

        sql = f"""DELETE FROM {self.table} WHERE (singer, album) in (VALUES
                    {','.join(values)}
                )
            """
        return self.query.exec(sql)
