# coding: utf-8
from typing import List

from common.database.entity import AlbumInfo, Playlist, SingerInfo, SongInfo
from common.library import Library
from common.style_sheet import setStyleSheet
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QStackedWidget, QWidget

from .album_interface import AlbumInterface
from .playlist_interface import PlaylistInterface
from .singer_interface import SingerInterface
from .song_interface import LocalSongInterface, OnlineSongInterface


class MoreSearchResultInterface(QWidget):
    """ More search result interface """

    playLocalSongSig = pyqtSignal(SongInfo)
    playOnlineSongSig = pyqtSignal(int)

    def __init__(self, library: Library, parent=None):
        super().__init__(parent=parent)
        self.resize(1270, 800)
        self.stackedWidget = QStackedWidget(self)
        self.albumInterface = AlbumInterface(library, self)
        self.singerInterface = SingerInterface(library, self)
        self.localSongInterface = LocalSongInterface([], self)
        self.onlineSongInterface = OnlineSongInterface([], self)
        self.playlistInterface = PlaylistInterface(library, self)
        self.titleMask = QWidget(self)
        self.titleLabel = QLabel(self)

        self.localSongListWidget = self.localSongInterface.songListWidget
        self.onlineSongListWidget = self.onlineSongInterface.songListWidget

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.titleLabel.move(30, 55)
        self.titleMask.setFixedHeight(125)
        self.stackedWidget.addWidget(self.albumInterface)
        self.stackedWidget.addWidget(self.singerInterface)
        self.stackedWidget.addWidget(self.playlistInterface)
        self.stackedWidget.addWidget(self.localSongInterface)
        self.stackedWidget.addWidget(self.onlineSongInterface)
        self.__setQss()
        self.__connectSignalToSlot()

    def resizeEvent(self, e):
        self.titleMask.resize(self.width()-10, 125)
        self.stackedWidget.resize(self.size())

    def updateWindow(self, keyWord: str, viewType: str, data: list):
        """ update window

        Parameters
        ----------
        keyWord: str
            key word

        viewType: str
            the type of displayed view, including：
            * `local song`: local song
            * `online song`: online song
            * `album`: local album
            * `singer`: local singer
            * `playlist`: local playlist

        data: list
            data to be displayed in view
        """
        funcMap = {
            'local song': self.showLocalSongInterface,
            'online song': self.showOnlineSongInterface,
            'album': self.showAlbumInterface,
            'singer': self.showSingerInterface,
            'playlist': self.showPlaylistInterface
        }

        if viewType not in funcMap:
            raise ValueError(f'The view type `{viewType}` is illegal')

        funcMap[viewType](keyWord, data)

    def showLocalSongInterface(self, keyWord: str, songInfos: List[SongInfo]):
        """ update and show local song interface """
        self.setTitle(f'"{keyWord}"'+self.tr('search result for local songs'))
        self.localSongInterface.updateWindow(songInfos)
        self.stackedWidget.setCurrentWidget(self.localSongInterface)

    def showAlbumInterface(self, keyWord: str, albumInfos: List[AlbumInfo]):
        """ update and show local album card interface """
        self.setTitle(f'"{keyWord}"'+self.tr('search result for albums'))
        self.albumInterface.updateWindow(albumInfos)
        self.stackedWidget.setCurrentWidget(self.albumInterface)

    def showPlaylistInterface(self, keyWord: str, playlists: List[Playlist]):
        """ update and show local playlist card interface """
        self.setTitle(f'"{keyWord}"'+self.tr('search result for playlists'))
        self.playlistInterface.updateWindow(playlists)
        self.stackedWidget.setCurrentWidget(self.playlistInterface)

    def showSingerInterface(self, keyWord: str, singerInfos: List[SingerInfo]):
        """ update and show local album card interface """
        self.setTitle(f'"{keyWord}"'+self.tr('search result for singers'))
        self.singerInterface.updateWindow(singerInfos)
        self.stackedWidget.setCurrentWidget(self.singerInterface)

    def showOnlineSongInterface(self, keyWord: str, songInfos: List[SongInfo]):
        """ update and show online song interface """
        self.setTitle(f'"{keyWord}"'+self.tr('search result for online songs'))
        self.onlineSongInterface.updateWindow(keyWord, songInfos)
        self.stackedWidget.setCurrentWidget(self.onlineSongInterface)

    def setTitle(self, title: str):
        """ set the title of interface """
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def __setQss(self):
        """ set style sheet """
        self.titleMask.setObjectName('mask')
        self.titleLabel.setObjectName('titleLabel')
        setStyleSheet(self, 'more_search_result_interface')

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.localSongListWidget.playSignal.connect(self.playLocalSongSig)
        self.onlineSongListWidget.playSignal.connect(self.playOnlineSongSig)
