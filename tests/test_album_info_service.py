# coding:utf-8
import sys

sys.path.append('app')

from PyQt5.QtSql import QSqlDatabase
from app.common.database.service import AlbumInfoService
from app.common.database.entity import AlbumInfo
from unittest import TestCase


class TestAlbumInfoService(TestCase):
    """ 测试专辑信息服务类 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.service = AlbumInfoService()
        self.albumInfos = [
            AlbumInfo(
                id='1'*32,
                singer='aiko',
                album='キラキラ',
                year=2005,
                genre='Pop',
                modifiedTime=1642818014664
            ),
            AlbumInfo(
                id='2'*32,
                singer='aiko',
                album='湿った夏の始まり',
                year=2016,
                genre='Pop',
                modifiedTime=1642818014664
            ),
            AlbumInfo(
                id='3'*32,
                singer='aiko',
                album='aikoの詩。',
                year=2019,
                genre='Pop',
                modifiedTime=1642818014664
            ),
            AlbumInfo(
                id='4'*32,
                singer='aiko',
                album='かばん',
                year=2004,
                genre='Pop',
                modifiedTime=1642818014664
            )
        ]
        # VS Code 的测试扩展会自动运行代码，导致缓存的数据丢失
        # self.service.clearTable()

    def test_create_table(self):
        """ 测试创建表格 """
        self.assertTrue(self.service.createTable())

    def test_add(self):
        """ 测试添加一条数据 """
        self.service.removeById(self.albumInfos[0].id)
        self.assertTrue(self.service.add(self.albumInfos[0]))

    def test_add_batch(self):
        """ 测试添加多条记录 """
        self.service.removeByIds([i.id for i in self.albumInfos[1:]])
        self.assertTrue(self.service.addBatch(self.albumInfos[1:]))

    def test_list_all(self):
        """ 测试查询所有专辑信息 """
        albumInfos = self.service.listAll()
        self.assertEqual(albumInfos, self.albumInfos)

    def test_remove_by_id(self):
        """ 测试移除一条数据 """
        self.assertTrue(self.service.removeById(self.albumInfos[0].id))

    def test_remove_by_ids(self):
        """ 测试移除多条数据 """
        self.assertTrue(self.service.removeByIds(
            [i.id for i in self.albumInfos[1:-1]]))

    def test_modify(self):
        """ 测试更新一个字段的值 """
        albumInfo = self.albumInfos[-1].copy()
        albumInfo.modifiedTime += 20
        self.assertTrue(self.service.modify(
            albumInfo.id, 'modifiedTime', albumInfo.modifiedTime))

    def test_modify_by_id(self):
        """ 测试通过 id 更新整行的值 """
        albumInfo = self.albumInfos[-1].copy()
        albumInfo.album = 'aikoの詩。'
        albumInfo.year = 2019
        albumInfo.modifiedTime += 10
        self.assertTrue(self.service.modifyById(albumInfo))
