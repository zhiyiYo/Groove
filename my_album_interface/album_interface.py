# coding:utf-8

import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QWidget

from my_dialog_box.album_info_edit_panel import AlbumInfoEditPanel

from .song_card_list_widget import SongCardListWidget
from .album_info_bar import AlbumInfoBar


class AlbumInterface(QWidget):
    """ 专辑界面 """
    saveAlbumInfoSig = pyqtSignal(dict, dict)
    playAlbumSignal = pyqtSignal(list)
    songCardPlaySig = pyqtSignal(int)
    nextToPlaySignal = pyqtSignal(dict)  # 下一首播放
    addSongToPlaylistSig = pyqtSignal(dict)  # 添加一首歌到正在播放
    addAlbumToPlaylistSig = pyqtSignal(list)  # 添加专辑到正在播放

    def __init__(self, albumInfo: dict, parent=None):
        super().__init__(parent)
        self.albumInfo = albumInfo
        self.songInfo_list = albumInfo.get('songInfo_list')  # type:list
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
        if albumInfo == self.albumInfo and not (albumInfo is self.albumInfo):
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

    def updateOneSongCard(self, oldSongInfo: dict, newSongInfo):
        """ 更新一个歌曲卡 """
        self.songListWidget.updateOneSongCard(oldSongInfo, newSongInfo)
        self.albumInfo['songInfo_list'] = self.songListWidget.songInfo_list

    def showAlbumInfoEditPanel(self):
        """ 显示专辑信息编辑面板 """
        oldAlbumInfo = self.albumInfo.copy()
        infoEditPanel = AlbumInfoEditPanel(self.albumInfo, self.window())
        infoEditPanel.saveInfoSig.connect(
            lambda newAlbumInfo: self.__saveAlbumInfoSlot(oldAlbumInfo, newAlbumInfo))
        infoEditPanel.setStyle(QApplication.style())
        infoEditPanel.exec_()

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 专辑信息栏信号
        self.albumInfoBar.playAllBt.clicked.connect(
            lambda: self.playAlbumSignal.emit(self.albumInfo.get('songInfo_list')))
        self.albumInfoBar.addToMenu.playingAct.triggered.connect(
            lambda: self.addAlbumToPlaylistSig.emit(self.songInfo_list))
        self.albumInfoBar.editInfoBt.clicked.connect(
            self.showAlbumInfoEditPanel)
        # 歌曲列表信号
        self.songListWidget.playSignal.connect(self.songCardPlaySig)
        self.songListWidget.nextToPlaySignal.connect(self.nextToPlaySignal)
        self.songListWidget.addSongToPlaylistSignal.connect(
            self.addSongToPlaylistSig)

    def sortSongCardsByTrackNum(self):
        """ 以曲序为基准排序歌曲卡 """
        self.songListWidget.sortSongCardByTrackNum()
        self.albumInfo['songInfo_list'] = self.songListWidget.songInfo_list
        self.songInfo_list = self.songListWidget.songCard_list

    def __saveAlbumInfoSlot(self, oldAlbumInfo: dict, newAlbumInfo: dict):
        """ 保存专辑信息 """
        self.saveAlbumInfoSig.emit(oldAlbumInfo, newAlbumInfo)
        self.updateWindow(newAlbumInfo)
        self.__sortSongCardsByTrackNum()
