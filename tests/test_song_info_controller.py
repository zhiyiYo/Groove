# coding:utf-8
import sys

sys.path.append('app')

from time import time
from unittest import TestCase

from app.common.database.controller import SongInfoController
from app.common.database.entity import SongInfo
from app.common.library import Directory
from PyQt5.QtSql import QSqlDatabase


class TestSongInfoController(TestCase):
    """ 测试歌曲信息控制类 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.controller = SongInfoController()
        self.directory = Directory('D:/hzz/音乐')

    def test_get_song_infos(self):
        """ 测试获取所有歌曲信息 """
        files = self.directory.glob()
        t0 = time()
        songInfos = self.controller.getSongInfosFromCache(files)
        t1 = time()
        print('耗时：', t1-t0)
        self.assertEqual(len(songInfos), len(files))
