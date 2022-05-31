# coding:utf-8
from typing import List

from PyQt5.QtCore import QDateTime
from PyQt5.QtSql import QSqlDatabase

from ..dao import RecentPlayDao
from ..entity import RecentPlay
from .service_base import ServiceBase


class RecentPlayService(ServiceBase):
    """ Recent play service """

    def __init__(self, db: QSqlDatabase = None):
        super().__init__()
        self.recentPlayDao = RecentPlayDao(db)

    def createTable(self) -> bool:
        return self.recentPlayDao.createTable()

    def clearTable(self) -> bool:
        return self.recentPlayDao.clearTable()

    def insertOrUpdate(self, file: str) -> bool:
        """ insert or update a recent played song record """
        recentPlay = self.recentPlayDao.selectBy(file=file)  # type:RecentPlay
        print(recentPlay)
        if not recentPlay:
            recentPlay = RecentPlay(
                file, QDateTime.currentDateTime().toSecsSinceEpoch())
        else:
            recentPlay.frequency += 1

        return self.recentPlayDao.insertOrUpdate(recentPlay)

    def findBy(self, **condition) -> RecentPlay:
        return self.recentPlayDao.selectBy(**condition)

    def listBy(self, **condition) -> List[RecentPlay]:
        return self.recentPlayDao.listBy(**condition)

    def listAll(self) -> List[RecentPlay]:
        return self.recentPlayDao.listAll()

    def setDatabase(self, db: QSqlDatabase):
        self.recentPlayDao.setDatabase(db)
