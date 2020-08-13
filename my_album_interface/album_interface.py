# coding:utf-8

import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QWidget

from .song_card_list_widget import SongCardListWidget
from .album_info_bar import AlbumInfoBar


class AlbumInterface(QWidget):
    """ 专辑界面 """
    playAlbumSignal = pyqtSignal(list)
    songCardPlaySig = pyqtSignal(int)
    nextToPlaySignal = pyqtSignal(dict)  # 下一首播放
    addSongToPlaylistSig = pyqtSignal(dict)  # 添加一首歌到正在播放
    addAlbumToPlaylistSig = pyqtSignal(list) # 添加专辑到正在播放

    def __init__(self, albumInfo: dict, parent=None):
        super().__init__(parent)
        self.albumInfo = albumInfo
        self.songInfo_list = albumInfo.get('songInfo_list')
        # 创建小部件
        self.albumInfoBar = AlbumInfoBar(albumInfo, self)
        self.songListWidget = SongCardListWidget(self.songInfo_list, self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1230, 900)
        self.setAutoFillBackground(True)
        self.songListWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.songListWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.songListWidget.move(30, 45 + self.albumInfoBar.height())
        palette = QPalette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
        # 信号连接到槽
        self.__connectSignalToSlot()

    def updateWindow(self, albumInfo: dict):
        """ 更新窗口 """
        if albumInfo == self.albumInfo:
            return
        self.albumInfo = albumInfo if albumInfo else {}
        self.songInfo_list = albumInfo.get('songInfo_list')
        self.albumInfoBar.updateWindow(albumInfo)
        self.songListWidget.updateSongCards(
            self.albumInfo.get('songInfo_list'))
        self.songListWidget.resize(
            self.width() - 60, self.height() - 45 - self.albumInfoBar.height())

    def resizeEvent(self, e):
        """ 改变尺寸时改变小部件大小 """
        super().resizeEvent(e)
        self.albumInfoBar.resize(
            self.width(), self.albumInfoBar.height())
        self.songListWidget.resize(
            self.width() - 60, self.height() - 45 - self.albumInfoBar.height())

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.albumInfoBar.playAllBt.clicked.connect(
            lambda: self.playAlbumSignal.emit(self.albumInfo.get('songInfo_list')))
        self.albumInfoBar.addToMenu.playingAct.triggered.connect(
            lambda:self.addAlbumToPlaylistSig.emit(self.songInfo_list))
        self.songListWidget.playSignal.connect(
            lambda index: self.songCardPlaySig.emit(index))
        self.songListWidget.nextToPlaySignal.connect(
            lambda songInfo: self.nextToPlaySignal.emit(songInfo))
        self.songListWidget.addSongToPlaylistSignal.connect(
            lambda songInfo: self.addSongToPlaylistSig.emit(songInfo))

    def updateOneSongCard(self, oldSongInfo:dict, newSongInfo):
        """ 更新一个歌曲卡 """
        self.songListWidget.updateOneSongCard(oldSongInfo,newSongInfo)
