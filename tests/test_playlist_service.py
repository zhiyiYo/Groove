# coding:utf-8
import sys
sys.path.append('app')

from unittest import TestCase
from app.common.database.entity import Playlist, SongInfo
from app.common.database.service import PlaylistService
from PyQt5.QtSql import QSqlDatabase


class TestPlaylistService(TestCase):
    """ 测试播放列表服务类 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.service = PlaylistService(self.db)
        self.playlists = [
            Playlist(
                'aiko',
                'aiko',
                'かばん',
                2,
                1,
                [SongInfo('aiko - かばん.mp3'), SongInfo('aiko - 秘密.mp3')]
            ),
            Playlist(
                '我喜欢',
                '鎖那',
                'tutu',
                2,
                2,
                [SongInfo('鎖那 - tutu.mp3'), SongInfo('aiko - 秘密.mp3')]
            ),
            Playlist(
                '日本歌',
                'RADWIMPS',
                '白日',
                2,
                1,
                [SongInfo('RADWIMPS - 白日.mp3'), SongInfo('aiko - Loveletter.mp3')]
            ),
            Playlist(
                '英文歌',
                'Charlie Puth',
                'Cheating on You',
                1,
                2,
                [SongInfo('Charlie Puth - Cheating on You.mp3')]
            ),
        ]
        # VS Code 的测试扩展会自动运行代码，导致缓存的数据丢失
        # self.service.clearTable()

    def test_create_table(self):
        """ 测试创建表格 """
        self.assertTrue(self.service.createTable())

    def test_add(self):
        """ 测试创建一个播放列表 """
        self.service.remove(self.playlists[0].name)
        self.assertTrue(self.service.add(self.playlists[0]))

    def test_modify(self):
        """ 测试修改一个播放列表 """
        self.assertTrue(self.service.modifyName('aiko', '柳井爱子'))

    def test_remove(self):
        """ 测试删除一个播放列表 """
        self.assertTrue(self.service.remove(self.playlists[0].name))
