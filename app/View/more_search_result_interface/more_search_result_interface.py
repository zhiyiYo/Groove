# coding: utf-8
from typing import List

from common.database.entity import AlbumInfo, SongInfo, Playlist
from common.library import Library
from PyQt5.QtCore import QFile, Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QStackedWidget, QWidget

from .album_interface import AlbumInterface
from .playlist_interface import PlaylistInterface
from .song_interface import LocalSongInterface


class MoreSearchResultInterface(QWidget):
    """ 更多搜索结果界面 """

    playLocalSongSig = pyqtSignal(SongInfo)

    def __init__(self, library: Library, parent=None):
        super().__init__(parent=parent)
        self.resize(1270, 800)
        self.stackedWidget = QStackedWidget(self)
        self.albumInterface = AlbumInterface(library, self)
        self.localSongInterface = LocalSongInterface([], self)
        self.playlistInterface = PlaylistInterface(library, self)
        self.titleMask = QWidget(self)
        self.titleLabel = QLabel(self)

        self.localSongListWidget = self.localSongInterface.songListWidget

        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.titleLabel.move(30, 55)
        self.titleMask.setFixedHeight(125)
        self.stackedWidget.addWidget(self.albumInterface)
        self.stackedWidget.addWidget(self.playlistInterface)
        self.stackedWidget.addWidget(self.localSongInterface)
        self.__setQss()
        self.__connectSignalToSlot()

    def resizeEvent(self, e):
        self.titleMask.resize(self.width()-10, 125)
        self.stackedWidget.resize(self.size())

    def updateWindow(self, keyWord: str, viewType: str, data: list):
        """ 更新窗口

        Parameters
        ----------
        keyWord: str
            关键词

        viewType: str
            显示的视图类型，有以下几种：
            * `local song`: 本地歌曲
            * `album`: 本地专辑
            * `playlist`: 本地播放列表

        data: list
            显示的数据
        """
        funcMap = {
            'local song': self.showLocalSongInterface,
            'album': self.showAlbumInterface,
            'playlist': self.showPlaylistInterface
        }

        if viewType not in funcMap:
            raise ValueError(f'`{viewType}` 非法')

        funcMap[viewType](keyWord, data)

    def showLocalSongInterface(self, keyWord: str, songInfos: List[SongInfo]):
        """ 更新并显示本地歌曲界面 """
        self.setTitle(f'"{keyWord}"'+self.tr('search result for local songs'))
        self.localSongInterface.updateWindow(songInfos)
        self.stackedWidget.setCurrentWidget(self.localSongInterface)

    def showAlbumInterface(self, keyWord: str, albumInfos: List[AlbumInfo]):
        """ 更新并显示专辑卡界面 """
        self.setTitle(f'"{keyWord}"'+self.tr('search result for albums'))
        self.albumInterface.updateWindow(albumInfos)
        self.stackedWidget.setCurrentWidget(self.albumInterface)

    def showPlaylistInterface(self, keyWord: str, playlists: List[Playlist]):
        """ 更新并显示播放列表卡界面 """
        self.setTitle(f'"{keyWord}"'+self.tr('search result for playlists'))
        self.playlistInterface.updateWindow(playlists)
        self.stackedWidget.setCurrentWidget(self.playlistInterface)

    def setTitle(self, title: str):
        """ 设置标题 """
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def __setQss(self):
        """ 设置层叠样式 """
        self.titleLabel.setObjectName('titleLabel')

        f = QFile(":/qss/more_search_result_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.localSongListWidget.playSignal.connect(self.playLocalSongSig)
