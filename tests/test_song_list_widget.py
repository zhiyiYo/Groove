# coding:utf-8
import sys

sys.path.append('app')

from unittest import TestCase

from app.common import resource
from app.common.database.entity import SongInfo
from app.View.my_music_interface.song_tab_interface import SongListWidget
from PyQt5.QtWidgets import QApplication


class TestSongCard(TestCase):
    """ 测试歌曲卡 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
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

    def test_run(self):
        """ 测试运行 """
        app = QApplication(sys.argv)
        w = SongListWidget([self.songInfo]*10)
        w.show()
        app.exec_()
