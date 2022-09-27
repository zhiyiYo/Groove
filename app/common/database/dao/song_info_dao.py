# coding:utf-8
from typing import List

from .dao_base import DaoBase
from ..entity import SongInfo


class SongInfoDao(DaoBase):
    """ Song information DAO """

    table = 'tbl_song_info'
    fields = ['file', 'title', 'singer', 'album', 'year', 'genre', 'duration', 'track',
              'trackTotal', 'disc', 'discTotal', 'createTime', 'modifiedTime']

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
        """ find song information by the path of audio file """
        return self.selectBy(file=file)

    def listBySingers(self, singers: List[str]) -> List[SongInfo]:
        """ list song information by singer name """
        if not singers:
            return []

        values = []
        orders = []
        for i, singer in enumerate(singers, 1):
            value = f"'{self.adjustText(singer)}'"
            values.append(value)
            orders.append(f"WHEN {value} THEN {i}")

        sql = f"""SELECT * FROM {self.table} WHERE singer in (
                {','.join(values)}
            )
            ORDER BY
                CASE singer
                {' '.join(orders)}
                END
            , album
            """
        if not self.query.exec(sql):
            return []

        return self.iterRecords()

    def listBySingerAlbum(self, singer: str, album: str) -> List[SongInfo]:
        """ list song information by singer name and album name """
        return self.listBy(singer=singer, album=album)

    def listBySingerAlbums(self, singers: List[str], albums: List[str]) -> List[SongInfo]:
        """ list song information by singer names and album names """
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


class PlaylistSongInfoDao(SongInfoDao):
    """ Playlist song information DAO """

    table = "tbl_playlist_song_info"
