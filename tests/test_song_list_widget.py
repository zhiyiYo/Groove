# coding:utf-8
import sys

sys.path.append('app')

from unittest import TestCase

from app.common import resource
from app.common.database.entity import SongInfo
from app.components.song_list_widget import SongListWidget as SongTabListWidget
from app.View.playing_interface.song_list_widget import \
    SongListWidget as PlayingSongListWidget
from PyQt5.QtWidgets import QApplication


class TestSongListWidget(TestCase):
    """ 测试歌曲列表控件 """

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

    def test_song_tab_list_widget(self):
        """ 测试我的音乐界面的歌曲列表课件 """
        app = QApplication(sys.argv)
        w = SongTabListWidget([self.songInfo]*10)
        w.show()
        app.exec_()

    def test_playing_list_widget(self):
        """ 测试正在界面的歌曲列表课件 """
        app = QApplication(sys.argv)
        w = PlayingSongListWidget([self.songInfo]*10)
        w.show()
        app.exec_()
