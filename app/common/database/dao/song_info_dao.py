# coding:utf-8
from pathlib import Path
from typing import List, Union

from PyQt5.QtSql import QSqlRecord

from .dao_base import DaoBase
from ..entity.song_info import SongInfo


class SongInfoDao(DaoBase):
    """ 歌曲信息数据库操作类 """

    table = 'tbl_song_info'

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

    def update(self, id: str, field: str, value) -> bool:
        sql = f"UPDATE {self.table} SET {field} = ? WHERE file = ?"
        self.query.prepare(sql)
        self.query.addBindValue(value)
        self.query.addBindValue(id)
        return self.query.exec()

    def updateById(self, entity: SongInfo) -> bool:
        sql = f"""UPDATE {self.table} SET
            title = ?,
            singer = ?,
            album = ?,
            year = ?,
            genre = ?,
            duration = ?,
            track = ?,
            trackTotal = ?,
            disc = ?,
            discTotal = ?,
            createTime = ?,
            modifiedTime = ?
            WHERE file = ?
        """
        self.query.prepare(sql)
        self.query.addBindValue(entity.title)
        self.query.addBindValue(entity.singer)
        self.query.addBindValue(entity.album)
        self.query.addBindValue(entity.year)
        self.query.addBindValue(entity.genre)
        self.query.addBindValue(entity.duration)
        self.query.addBindValue(entity.track)
        self.query.addBindValue(entity.trackTotal)
        self.query.addBindValue(entity.disc)
        self.query.addBindValue(entity.discTotal)
        self.query.addBindValue(entity.createTime)
        self.query.addBindValue(entity.modifiedTime)
        self.query.addBindValue(entity.file)
        return self.query.exec()

    def insert(self, entity: SongInfo) -> bool:
        sql = f"""INSERT INTO {self.table} VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """
        self.query.prepare(sql)
        self.query.addBindValue(self.adjustText(entity.file))
        self.query.addBindValue(self.adjustText(entity.title))
        self.query.addBindValue(self.adjustText(entity.singer))
        self.query.addBindValue(self.adjustText(entity.album))
        self.query.addBindValue(entity.year)
        self.query.addBindValue(self.adjustText(entity.genre))
        self.query.addBindValue(entity.duration)
        self.query.addBindValue(entity.track)
        self.query.addBindValue(entity.trackTotal)
        self.query.addBindValue(entity.disc)
        self.query.addBindValue(entity.discTotal)
        self.query.addBindValue(entity.createTime)
        self.query.addBindValue(entity.modifiedTime)
        return self.query.exec()

    def insertBatch(self, entities: List[SongInfo]) -> bool:
        if not entities:
            return True

        values = []
        for songInfo in entities:
            value = f"""(
                '{self.adjustText(songInfo.file)}',
                '{self.adjustText(songInfo.title)}',
                '{self.adjustText(songInfo.singer)}',
                '{self.adjustText(songInfo.album)}',
                {songInfo.year},
                '{self.adjustText(songInfo.genre)}',
                {songInfo.duration},
                {songInfo.track},
                {songInfo.trackTotal},
                {songInfo.disc},
                {songInfo.discTotal},
                {songInfo.createTime},
                {songInfo.modifiedTime}
            )"""
            values.append(value)

        sql = f"INSERT INTO {self.table} VALUES {','.join(values)}"
        return self.query.exec(sql)

    def deleteById(self, id: str) -> bool:
        sql = f"DELETE FROM {self.table} WHERE file = ?"
        self.query.prepare(sql)
        self.query.addBindValue(id)
        return self.query.exec()

    def deleteByIds(self, ids: List[str]) -> bool:
        if not ids:
            return True

        placeHolders = ','.join(['?']*len(ids))
        sql = f"DELETE FROM {self.table} WHERE file IN ({placeHolders})"
        self.query.prepare(sql)
        for id in ids:
            self.query.addBindValue(id)

        return self.query.exec()

    @staticmethod
    def loadFromRecord(record: QSqlRecord) -> SongInfo:
        songInfo = SongInfo()

        for i in range(record.count()):
            field = record.fieldName(i)
            songInfo[field] = record.value(i)

        return songInfo
