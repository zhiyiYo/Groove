# coding:utf-8
import sys
sys.path.append('app')

from unittest import TestCase
from app.common.database.service import SongInfoService
from app.common.database.entity import SongInfo
from PyQt5.QtSql import QSqlDatabase


class TestSongInfoService(TestCase):
    """ 测试歌曲信息服务类 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.service = SongInfoService()
        self.songInfo = SongInfo(
            file='D:/hzz/音乐/aiko - キラキラ.mp3',
            title='キラキラ',
            singer='aiko',
            album='キラキラ',
            year=2005,
            genre='Pop',
            duration=307,
            track=1,
            trackTotal=4,
            disc=1,
            discTotal=1,
            createTime=1642818014664,
            modifiedTime=1642818014664
        )

    def test_create_table(self):
        """ 测试创建表格 """
        self.assertTrue(self.service.createTable())

    def test_add(self):
        """ 测试添加一条数据 """
        self.service.removeById(self.songInfo.file)
        self.assertTrue(self.service.add(self.songInfo))

    def test_add_batch(self):
        """ 测试添加多条记录 """
        songInfos = [
            SongInfo(
                file="D:/hzz/音乐/aiko - KissHug.mp3",
                title='KissHug',
                singer='aiko',
                album='aikoの詩。',
                year=2019,
                genre='Pop',
                duration=303,
                track=2,
                trackTotal=56,
                disc=1,
                discTotal=4,
                createTime=1642818014664,
                modifiedTime=1642818014664
            ),
            SongInfo(
                file="D:/hzz/音乐/aiko - Loveletter.mp3",
                title='Loveletter',
                singer='aiko',
                album='aikoの詩。',
                year=2019,
                genre='Pop',
                duration=296,
                track=41,
                trackTotal=56,
                disc=1,
                discTotal=4,
                createTime=1642818014664,
                modifiedTime=1642818014664
            ),
        ]
        self.service.removeByIds([i.file for i in songInfos])
        self.assertTrue(self.service.addBatch(songInfos))

    def test_find_by_file(self):
        """ 测试通过文件路径查找歌曲信息 """
        self.assertEqual(self.service.findByFile(
            self.songInfo.file), self.songInfo)

    def test_list_all(self):
        """ 测试查询所有歌曲信息 """
        songInfos = self.service.listAll()
        self.assertEqual(len(songInfos), 3)

    def test_list_by_singer_album(self):
        """ 测试通过歌手和专辑查询所有歌曲 """
        songInfos = self.service.listBySingerAlbum('aiko', 'aikoの詩。')
        self.assertEqual(len(songInfos), 2)

    def test_remove_by_id(self):
        """ 测试移除一条数据 """
        self.assertTrue(self.service.removeById(self.songInfo.file))

    def test_remove_by_ids(self):
        """ 测试移除多条数据 """
        self.assertTrue(self.service.removeByIds([self.songInfo.file]))

    def test_modify(self):
        """ 测试更新一个字段的值 """
        songInfo = SongInfo(
            file='D:/hzz/音乐/aiko - かばん.mp3',
            title='かばん',
            singer='aiko',
            album='かばん',
            year=2005,
            genre='Pop',
            duration=290,
            track=1,
            trackTotal=4,
            disc=1,
            discTotal=1,
            createTime=1642818014664,
            modifiedTime=1642818014664
        )
        self.service.add(songInfo)

        songInfo.modifiedTime += 10
        self.assertTrue(self.service.modify(
            songInfo.file, 'modifiedTime', songInfo.modifiedTime))

    def test_modify_by_id(self):
        """ 测试通过 id 更新整行的值 """
        songInfo = SongInfo(
            file='D:/hzz/音乐/aiko - かばん.mp3',
            title='かばん',
            singer='aiko',
            album='かばん',
            year=2004,
            genre='Pop',
            duration=290,
            track=1,
            trackTotal=4,
            disc=1,
            discTotal=1,
            createTime=1642818014664,
            modifiedTime=1642818014664
        )
        self.service.add(songInfo)

        songInfo.album = 'aikoの詩。'
        songInfo.year = 2019
        songInfo.track = 3
        songInfo.trackTotal = 56
        songInfo.discTotal = 4
        songInfo.modifiedTime += 10
        self.assertTrue(self.service.modifyById(songInfo))
