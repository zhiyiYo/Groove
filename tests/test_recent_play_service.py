# coding:utf-8
import sys
sys.path.append('app')

from unittest import TestCase
from app.common.database.entity import RecentPlay
from app.common.database.service import RecentPlayService
from PyQt5.QtSql import QSqlDatabase


class TestRecentPlayService(TestCase):
    """ 测试最近播放服务类 """

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.service = RecentPlayService(self.db)
        # VS Code 的测试扩展会自动运行代码，导致缓存的数据丢失
        # self.service.clearTable()

    def test_create_table(self):
        """ 测试创建表格 """
        self.assertTrue(self.service.createTable())

    def test_insert_or_update(self):
        """ 测试创建或插入最近播放记录 """
        files = [
            'D:/hzz/音乐/aiko - キラキラ.mp3',
            'D:/hzz/音乐/aiko - KissHug.mp3',
            'D:/hzz/音乐/aiko - キラキラ.mp3',
        ]
        for file in files:
            self.assertTrue(self.service.insertOrUpdate(file))

        recent_play = self.service.findBy(file=files[0])
        self.assertIsNotNone(recent_play)
        self.assertEqual(recent_play.frequency, 2)

