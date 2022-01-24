# coding:utf-8
import sys

sys.path.append('app')

from unittest import TestCase

from app.common.database.entity import AlbumInfo
from app.common.database.service import AlbumInfoService
from PyQt5.QtSql import QSqlDatabase


class TestAlbumInfoService(TestCase):
    """ 测试专辑信息服务类 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.service = AlbumInfoService()
        self.albumInfo = AlbumInfo(
            id='1'*32,
            singer='aiko',
            album='キラキラ',
            year=2005,
            genre='Pop',
            modifiedTime=1642818014664
        )
        self.service.clearTable()

    def test_singleton(self):
        """ 测试歌曲信息服务是否为单例 """
        self.assertTrue(self.service is AlbumInfoService())

    def test_create_table(self):
        """ 测试创建表格 """
        self.assertTrue(self.service.createTable())

    def test_add(self):
        """ 测试添加一条数据 """
        self.service.removeById(self.albumInfo.id)
        self.assertTrue(self.service.add(self.albumInfo))

    def test_add_batch(self):
        """ 测试添加多条记录 """
        albumInfos = [
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
        ]
        self.service.removeByIds([i.id for i in albumInfos])
        self.assertTrue(self.service.addBatch(albumInfos))

    def test_list_all(self):
        """ 测试查询所有专辑信息 """
        albumInfos = self.service.listAll()
        self.assertEqual(len(albumInfos), 3)

    def test_remove_by_id(self):
        """ 测试移除一条数据 """
        self.assertTrue(self.service.removeById(self.albumInfo.id))

    def test_remove_by_ids(self):
        """ 测试移除多条数据 """
        self.assertTrue(self.service.removeByIds(['2'*32, '3'*32]))

    def test_modify(self):
        """ 测试更新一个字段的值 """
        albumInfo = AlbumInfo(
            id='4'*32,
            singer='aiko',
            album='かばん',
            year=2005,
            genre='Pop',
            modifiedTime=1642818014664
        )
        self.service.add(albumInfo)

        albumInfo.modifiedTime += 20
        self.assertTrue(self.service.modify(
            albumInfo.id, 'modifiedTime', albumInfo.modifiedTime))

    def test_modify_by_id(self):
        """ 测试通过 id 更新整行的值 """
        albumInfo = AlbumInfo(
            id='4'*32,
            singer='aiko',
            album='かばん',
            year=2004,
            genre='Pop',
            modifiedTime=1642818014664
        )
        self.service.add(albumInfo)

        albumInfo.album = 'aikoの詩。'
        albumInfo.year = 2019
        albumInfo.modifiedTime += 10
        self.assertTrue(self.service.modifyById(albumInfo))
