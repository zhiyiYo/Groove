# coding:utf-8
from typing import List

from common.config import config
from PyQt5.QtSql import QSqlDatabase

from ..entity import SongInfo
from ..service import RecentPlayService, SongInfoService


class RecentPlayController:
    """ Recent play controller """

    def __init__(self, db: QSqlDatabase = None):
        self.recentPlayService = RecentPlayService(db)
        self.songInfoService = SongInfoService(db)

    def getRecentPlays(self, key='lastPlayedTime') -> List[SongInfo]:
        """ get all recent plays """
        recentPlays = self.recentPlayService.listBy(
            orderBy=key, desc=True, limit=config['recent-plays-number'])
        return self.songInfoService.listByIds([i.file for i in recentPlays])

    def add(self, file: str) -> bool:
        """ add a recent play record """
        return self.recentPlayService.insertOrUpdate(file)

    def delete(self, name: str):
        """ delete a recent play record """
        return self.recentPlayService.removeById(name)

    def deleteBatch(self, names: List[str]):
        """ delete multi recent play records """
        return self.recentPlayService.removeByIds(names)
