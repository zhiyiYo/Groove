# coding:utf-8
from typing import List

from PyQt5.QtSql import QSqlDatabase

from ..entity import SongInfo
from ..service import RecentPlayService, SongInfoService


class RecentPlayController:
    """ Recent play controller """

    def __init__(self, db: QSqlDatabase = None):
        self.recentPlayService = RecentPlayService(db)
        self.songInfoService = SongInfoService(db)

    def getRecentPlays(self) -> List[SongInfo]:
        """ get all recent plays """
        recentPlays = self.recentPlayService.listAll()
        recentPlays.sort(key=lambda i: i.lastPlayedTime, reverse=True)
        return self.songInfoService.listByIds([i.file for i in recentPlays])

    def add(self, file: str) -> bool:
        """ add a recent play record """
        return self.recentPlayService.insertOrUpdate(file)