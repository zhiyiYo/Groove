# coding:utf-8
from typing import List

from PyQt5.QtSql import QSqlRecord

from .dao_base import DaoBase
from ..entity.song_info import SongInfo


class SongInfoDao(DaoBase):
    """ 歌曲信息数据库操作类 """

    table = 'tbl_song_info'
    fields = ['file', 'title', 'singer', 'album', 'year', 'genre', 'duration', 'track',
              'trackTotal', 'disc', 'discTotal', 'createTime', 'modifiedTime']

    def __init__(self):
        super().__init__()

    def createTable(self):
        success = self.query.exec(f"""
            CREATE TABLE IF NOT EXISTS {self.table}(
                file TEXT PRIMARY KEY,
                title TEXT,
                singer TEXT,
                album TEXT,
                year YEAR,
                genre TEXT,
                duration INTEGER,
                track INTEGER,
                trackTotal INTEGER,
                disc INTEGER,
                discTotal INTEGER,
                createTime INTEGER,
                modifiedTime INTEGER
            )
        """)
        return success

    def selectByFile(self, file: str) -> SongInfo:
        """ 通过文件路径查找 """
        return self.selectBy(file=file)

    def listBySingerAlbum(self, singer: str, album: str) -> List[SongInfo]:
        """ 通过歌手和专辑查询 """
        return self.listBy(singer=singer, album=album)

    def listBySongerAlbums(self, singers: List[str], albums: List[str]) -> List[SongInfo]:
        """ 通过歌手和专辑列表查询 """
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
                , track
            """
        if not self.query.exec(sql):
            return []

        return self.iterRecords()

    @staticmethod
    def loadFromRecord(record: QSqlRecord) -> SongInfo:
        songInfo = SongInfo()

        for i in range(record.count()):
            field = record.fieldName(i)
            songInfo[field] = record.value(i)

        return songInfo
