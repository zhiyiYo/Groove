# coding:utf-8
from typing import List

from PyQt5.QtSql import QSqlDatabase

from ..dao import SingerInfoDao
from ..entity import SingerInfo

from.service_base import ServiceBase


class SingerInfoService(ServiceBase):
    """ Singer information service """

    def __init__(self, db: QSqlDatabase = None):
        super().__init__()
        self.singerInfoDao = SingerInfoDao(db)

    def createTable(self) -> bool:
        return self.singerInfoDao.createTable()

    def findBy(self, **condition) -> SingerInfo:
        return self.singerInfoDao.selectBy(**condition)

    def listBy(self, **condition) -> List[SingerInfo]:
        return self.singerInfoDao.listBy(**condition)

    def listAll(self) -> List[SingerInfo]:
        return self.singerInfoDao.listAll()

    def listByIds(self, ids: List[str]) -> List[SingerInfo]:
        return self.singerInfoDao.listByIds(ids)

    def modify(self, id: str, field: str, value) -> bool:
        return self.singerInfoDao.update(id, field, value)

    def modifyById(self, singerInfo: SingerInfo) -> bool:
        return self.singerInfoDao.updateById(singerInfo)

    def modifyByIds(self, singerInfos: List[SingerInfo]) -> bool:
        return self.singerInfoDao.updateByIds(singerInfos)

    def add(self, singerInfo: SingerInfo) -> bool:
        return self.singerInfoDao.insert(singerInfo)

    def addBatch(self, singerInfos: List[SingerInfo]) -> bool:
        return self.singerInfoDao.insertBatch(singerInfos)

    def removeById(self, id: str) -> bool:
        return self.singerInfoDao.deleteById(id)

    def removeByIds(self, ids: List[str]) -> bool:
        return self.singerInfoDao.deleteByIds(ids)

    def clearTable(self) -> bool:
        return self.singerInfoDao.clearTable()

    def setDatabase(self, db: QSqlDatabase):
        self.singerInfoDao.setDatabase(db)

    def listLike(self, **condition) -> List[SingerInfo]:
        return self.singerInfoDao.listLike(**condition)
