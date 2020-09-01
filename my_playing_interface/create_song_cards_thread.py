# coding:utf-8

from PyQt5.QtCore import QThread, pyqtSignal

from .song_list_widget import SongListWidget, UpdateMode


class CreateSongCardsThread(QThread):
    """ 创建歌曲卡线程 """
    createDone = pyqtSignal()

    def __init__(self, songListWidget, parent=None):
        super().__init__(parent)
        self.songListWidget = songListWidget  # type:SongListWidget
        self.playlist = None
        self.__isResetIndex=True

    def setPlaylist(self, playlist,isResetIndex:bool=True):
        """ 更新播放列表 """
        self.playlist = playlist
        self.__isResetIndex = isResetIndex

    def run(self):
        """ 创建歌曲卡 """
        if self.songListWidget.updateMode == UpdateMode.CREATE_ALL_NEW_CARDS:
            self.songListWidget.createSongCards()
            self.createDone.emit()
        elif self.songListWidget.updateMode == UpdateMode.UPDATE_ALL_CARDS:
            self.songListWidget.updateSongCards(self.playlist,self.__isResetIndex)
