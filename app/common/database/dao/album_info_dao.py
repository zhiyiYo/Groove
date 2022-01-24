# coding:utf-8
from pathlib import Path
from typing import List, Union

from PyQt5.QtSql import QSqlRecord

from .dao_base import DaoBase
from ..entity.album_info import AlbumInfo


class AlbumInfoDao(DaoBase):
    """ 专辑信息数据库操作类 """

    table = 'tbl_album_info'

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

    def update(self, id: str, field: str, value) -> bool:
        sql = f"UPDATE {self.table} SET {field} = ? where id = ?"
        self.query.prepare(sql)
        self.query.addBindValue(value)
        self.query.addBindValue(id)
        return self.query.exec()

    def updateById(self, entity: AlbumInfo) -> bool:
        sql = f"""UPDATE {self.table} SET
            singer = ?,
            album = ?,
            year = ?,
            genre = ?,
            modifiedTime = ?
            WHERE id = ?
        """
        self.query.prepare(sql)
        self.query.addBindValue(self.adjustText(entity.singer))
        self.query.addBindValue(self.adjustText(entity.album))
        self.query.addBindValue(entity.year)
        self.query.addBindValue(self.adjustText(entity.genre))
        self.query.addBindValue(entity.modifiedTime)
        self.query.addBindValue(entity.id)
        return self.query.exec()

    def insert(self, entity: AlbumInfo) -> bool:
        sql = f"INSERT INTO {self.table} VALUES (?, ?, ?, ?, ?, ?)"
        self.query.prepare(sql)
        self.query.addBindValue(self.adjustText(entity.id))
        self.query.addBindValue(self.adjustText(entity.singer))
        self.query.addBindValue(self.adjustText(entity.album))
        self.query.addBindValue(entity.year)
        self.query.addBindValue(self.adjustText(entity.genre))
        self.query.addBindValue(entity.modifiedTime)
        return self.query.exec()

    def insertBatch(self, entities: List[AlbumInfo]) -> bool:
        if not entities:
            return True

        values = []
        for albumInfo in entities:
            value = f"""(
                '{self.adjustText(albumInfo.id)}',
                '{self.adjustText(albumInfo.singer)}',
                '{self.adjustText(albumInfo.album)}',
                {albumInfo.year},
                '{self.adjustText(albumInfo.genre)}',
                {albumInfo.modifiedTime}
            )"""
            values.append(value)

        sql = f"INSERT INTO {self.table} VALUES {','.join(values)}"
        return self.query.exec(sql)

    def deleteById(self, id: str) -> bool:
        sql = f"DELETE FROM {self.table} WHERE id = ?"
        self.query.prepare(sql)
        self.query.addBindValue(id)
        return self.query.exec()

    def deleteByIds(self, ids: List[str]) -> bool:
        if not ids:
            return True

        placeHolders = ','.join(['?']*len(ids))
        sql = f"DELETE FROM {self.table} WHERE id IN ({placeHolders})"
        self.query.prepare(sql)
        for id in ids:
            self.query.addBindValue(id)

        return self.query.exec()

    @staticmethod
    def loadFromRecord(record: QSqlRecord) -> AlbumInfo:
        albumInfo = AlbumInfo()

        for i in range(record.count()):
            field = record.fieldName(i)
            albumInfo[field] = record.value(i)

        return albumInfo
