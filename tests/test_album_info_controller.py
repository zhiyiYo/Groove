# coding:utf-8
import sys

sys.path.append('app')

from time import time
from unittest import TestCase

from app.common.database.controller import (AlbumInfoController,
                                            SongInfoController)
from app.common.database.entity import SongInfo, AlbumInfo
from app.common.library import Directory
from PyQt5.QtSql import QSqlDatabase


class TestAlbumInfoController(TestCase):
    """ 测试专辑信息控制类 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.songInfoController = SongInfoController()
        self.albumInfoController = AlbumInfoController()
        self.directory = Directory('D:/hzz/音乐')

    def test_get_album_infos(self):
        """ 测试获取所有专辑信息 """
        files = self.directory.glob()
        t0 = time()
        songInfos = self.songInfoController.getSongInfosFromCache(files)
        albumInfos = self.albumInfoController.getAlbumInfosFromCache(songInfos)
        t1 = time()
        print('耗时：', t1-t0)

        albums = set(i.singer+'_'+i.album for i in songInfos)
        self.assertEqual(len(albumInfos), len(albums))
