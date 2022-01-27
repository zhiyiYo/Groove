# coding:utf-8
import sys
sys.path.append('app')

from PyQt5.QtSql import QSqlDatabase
from app.common.database.service import SingerInfoService
from app.common.database.entity import SingerInfo
from unittest import TestCase


class TestSingerInfoService(TestCase):
    """ 测试歌手信息服务类 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.service = SingerInfoService()
        self.singerInfos = [
            SingerInfo(id='1'*32, singer='aiko', genre='Pop'),
            SingerInfo(id='2'*32, singer='RADWIMPS', genre='J-Pop'),
            SingerInfo(id='3'*32, singer='鎖那', genre='Pop'),
            SingerInfo(id='4'*32, singer='halca', genre='Pop')
        ]
        # VS Code 的测试扩展会自动运行代码，导致缓存的数据丢失
        # self.service.clearTable()

    def test_create_table(self):
        """ 测试创建表格 """
        self.assertTrue(self.service.createTable())

    def test_add(self):
        """ 测试添加一条数据 """
        self.service.removeById(self.singerInfos[0].id)
        self.assertTrue(self.service.add(self.singerInfos[0]))

    def test_add_batch(self):
        """ 测试添加多条记录 """
        self.service.removeByIds([i.id for i in self.singerInfos[1:]])
        self.assertTrue(self.service.addBatch(self.singerInfos[1:]))

    def test_list_all(self):
        """ 测试查询所有专辑信息 """
        singerInfos = self.service.listAll()
        self.assertEqual(singerInfos, self.singerInfos)

    def test_remove_by_id(self):
        """ 测试移除一条数据 """
        self.assertTrue(self.service.removeById(self.singerInfos[0].id))

    def test_remove_by_ids(self):
        """ 测试移除多条数据 """
        self.assertTrue(self.service.removeByIds(
            [i.id for i in self.singerInfos[1:-1]]))

    def test_modify(self):
        """ 测试更新一个字段的值 """
        singerInfo = self.singerInfos[-1]
        self.assertTrue(self.service.modify(singerInfo.id, 'genre', 'Pop'))

    def test_modify_by_id(self):
        """ 测试通过 id 更新整行的值 """
        singerInfo = self.singerInfos[-1].copy()
        singerInfo.genre = 'POP'
        self.assertTrue(self.service.modifyById(singerInfo))
