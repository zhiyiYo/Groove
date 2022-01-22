# coding:utf-8
import sys
sys.path.append('app')

from PyQt5.QtSql import QSqlDatabase
from app.common.library import Directory
from app.common.database.entity import SongInfo
from app.common.database.controller import SongInfoController
from unittest import TestCase
from time import time


class TestSongInfoService(TestCase):
    """ 测试歌曲信息服务类 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.controller = SongInfoController()
        self.directory = Directory('./app/resource/test_audio')

    def test_get_song_infos(self):
        """ 测试获取所有歌曲信息 """
        files = self.directory.glob()
        songInfos = self.controller.getSongInfos(files)
        self.assertEqual(len(songInfos), 33)
