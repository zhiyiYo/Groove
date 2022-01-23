# coding:utf-8
import sys
sys.path.append('app')

from PyQt5.QtSql import QSqlDatabase
from app.common.library import Library, Directory
from app.common.database.entity import SongInfo
from unittest import TestCase
from time import time


class TestLibrary(TestCase):
    """ 测试歌曲库 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.library = Library(['D:/hzz/音乐'])

    def test_load(self):
        """ 测试载入音乐 """
        directory = Directory('D:/hzz/音乐')
        files = directory.glob()
        self.library.load()
        self.assertEqual(len(self.library.songInfos), len(files))