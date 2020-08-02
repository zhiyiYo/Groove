# coding:utf-8

import sys
from enum import Enum

from PyQt5.QtCore import Qt, QThread,pyqtSignal
from PyQt5.QtWidgets import QApplication

from .song_list_widget import SongListWidget, UpdateMode


class CreateSongCardsThread(QThread):
    """ 创建歌曲卡线程 """
    createDone = pyqtSignal()

    def __init__(self, songListWidget, parent=None):
        super().__init__(parent)
        self.songListWidget = songListWidget  # type:SongListWidget
        self.playlist = None

    def setPlaylist(self, playlist):
        """ 更新播放列表 """
        self.playlist = playlist

    def run(self):
        """ 创建歌曲卡 """
        if self.songListWidget.updateMode == UpdateMode.CREATE_ALL_NEW_CARDS:
            self.songListWidget.createSongCards()
            self.createDone.emit()
        elif self.songListWidget.updateMode == UpdateMode.UPDATE_ALL_CARDS:
            self.songListWidget.updateSongCards(self.playlist)
