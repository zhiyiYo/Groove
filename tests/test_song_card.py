# coding:utf-8
from PyQt5.QtWidgets import QApplication
from app.components.song_list_widget.song_card import (
    AlbumInterfaceSongCard, NoCheckBoxSongCard, OnlineSongCard,
    PlaylistInterfaceSongCard, SongTabSongCard)
from app.common.style_sheet import setStyleSheet
from app.common.database.entity import SongInfo
from app.common import resource
from unittest import TestCase
import sys

sys.path.append('app')


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

    def test_song_tab_song_card(self):
        """ 测试我的音乐歌曲界面的歌曲卡 """
        app = QApplication(sys.argv)
        w = SongTabSongCard(self.songInfo)
        setStyleSheet(w, 'song_list_widget')
        w.show()
        app.exec_()

    def test_album_interface_song_card(self):
        """ 测试专辑界面歌曲卡 """
        app = QApplication(sys.argv)
        w = AlbumInterfaceSongCard(self.songInfo)
        setStyleSheet(w, 'song_list_widget')
        w.show()
        app.exec_()

    def test_playlist_interface_song_card(self):
        """ 测试播放列表界面歌曲卡 """
        app = QApplication(sys.argv)
        w = PlaylistInterfaceSongCard(self.songInfo)
        setStyleSheet(w, 'song_list_widget')
        w.show()
        app.exec_()

    def test_no_check_box_song_card(self):
        """ 测试没有复选框的歌曲卡 """
        app = QApplication(sys.argv)
        w = NoCheckBoxSongCard(self.songInfo)
        setStyleSheet(w, 'song_list_widget')
        w.show()
        app.exec_()

    def test_online_song_card(self):
        """ 测试在线歌曲卡 """
        app = QApplication(sys.argv)
        w = OnlineSongCard(self.songInfo)
        setStyleSheet(w, 'song_list_widget')
        w.show()
        app.exec_()
