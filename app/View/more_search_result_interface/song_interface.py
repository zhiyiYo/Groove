# coding:utf-8
from math import ceil
from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QAction
from common.crawler import QueryServerType
from common.database.entity import SongInfo
from common.style_sheet import setStyleSheet
from common.signal_bus import signalBus
from common.thread.search_online_songs_thread import SearchOnlineSongsThread
from components.selection_mode_interface import (SelectionModeBarType,
                                                 SongSelectionModeInterface)
from components.song_list_widget import SongListWidget, NoScrollSongListWidget, SongCardType
from components.song_list_widget.song_card import OnlineSongCard
from components.widgets.menu import RoundMenu, DownloadMenu, AddToMenu


class OnlineSongListContextMenu(RoundMenu):
    """ Online song list widget context menu """

    def __init__(self, parent):
        super().__init__("", parent)
        self.setObjectName('onlineSongListContextMenu')
        self.playAct = QAction(self.tr("Play"), self)
        self.nextSongAct = QAction(self.tr("Play next"), self)
        self.viewOnlineAct = QAction(self.tr('View online'), self)
        self.showPropertyAct = QAction(self.tr("Properties"), self)
        self.downloadMenu = DownloadMenu(self.tr('Download'), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        self.addActions([self.playAct, self.nextSongAct])
        self.addMenu(self.addToMenu)
        self.addAction(self.viewOnlineAct)
        self.addMenu(self.downloadMenu)
        self.addAction(self.showPropertyAct)
        self.addSeparator()
        self.addAction(self.selectAct)


class OnlineSongListWidget(NoScrollSongListWidget):
    """ Online song list widget """

    def __init__(self, songInfos: List[SongInfo], parent=None):
        super().__init__(songInfos, SongCardType.ONLINE_SONG_CARD, parent)
        setStyleSheet(self, 'song_list_widget')

    def contextMenuEvent(self, e):
        hitIndex = self.indexAt(e.pos()).column()
        if hitIndex > -1:
            menu = OnlineSongListContextMenu(self)
            self.__connectContextMenuSignalToSlot(menu)
            menu.exec(self.cursor().pos())

    def _connectSongCardSignalToSlot(self, songCard: OnlineSongCard):
        songCard.doubleClicked.connect(lambda i: self._playSongs(i))
        songCard.playButtonClicked.connect(lambda i: self._playSongs(i))
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.checkedStateChanged.connect(
            self.onSongCardCheckedStateChanged)

    def __connectContextMenuSignalToSlot(self, menu: OnlineSongListContextMenu):
        menu.showPropertyAct.triggered.connect(
            self.showSongPropertyDialog)
        menu.playAct.triggered.connect(
            lambda: signalBus.playOneSongCardSig.emit(self.currentSongInfo))
        menu.nextSongAct.triggered.connect(
            lambda: signalBus.nextToPlaySig.emit([self.currentSongInfo]))
        menu.downloadMenu.downloadSig.connect(
            lambda quality: signalBus.downloadSongSig.emit(self.currentSongInfo, quality))
        menu.viewOnlineAct.triggered.connect(
            lambda: signalBus.getSongDetailsUrlSig.emit(self.currentSongInfo, QueryServerType.KUWO))
        menu.selectAct.triggered.connect(
            lambda: self.currentSongCard.setChecked(True))

        menu.addToMenu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit([self.currentSongInfo]))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, [self.currentSongInfo]))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.currentSongInfo]))


class LocalSongInterface(SongSelectionModeInterface):
    """ Local song interface """

    def __init__(self, songInfos: List[SongInfo], parent=None):
        super().__init__(SongListWidget(songInfos), SelectionModeBarType.SONG_TAB, parent)
        self.resize(1270, 800)
        self.vBox.setContentsMargins(0, 145, 0, 0)
        self.__connectSignalToSlot()

    def updateWindow(self, songInfos: List[SongInfo]):
        """ update window """
        self.songListWidget.updateAllSongCards(songInfos)
        self.adjustScrollHeight()

    def deleteSongs(self, songPaths: List[str]):
        """ delete songs """
        self.songListWidget.removeSongCards(songPaths)
        self.adjustScrollHeight()

    def __play(self, songInfo: SongInfo):
        """ play songs """
        index = self.songListWidget.songInfos.index(songInfo)
        signalBus.playPlaylistSig.emit(self.songListWidget.songInfos, index)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.songListWidget.playSignal.connect(self.__play)
        self.songListWidget.removeSongSignal.connect(
            lambda songInfo: signalBus.removeSongSig.emit([songInfo.file]))


class OnlineSongInterface(SongSelectionModeInterface):
    """ Online song interface """

    def __init__(self, songInfos: List[SongInfo], parent=None):
        super().__init__(OnlineSongListWidget(songInfos),
                         SelectionModeBarType.ONLINE_SONG, parent)
        self.resize(1270, 800)
        self.vBox.setContentsMargins(0, 145, 0, 0)
        self.searchThread = SearchOnlineSongsThread(self.window())
        self.__connectSignalToSlot()

    def updateWindow(self, keyWord: str, songInfos: List[SongInfo]):
        """ update window """
        self.searchThread.setKeyWord(keyWord)
        self.songListWidget.updateAllSongCards(songInfos)
        self.adjustScrollHeight()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.searchThread.searchFinished.connect(self.__loadMoreSongs)
        self.verticalScrollBar().valueChanged.connect(self.__onScrollValueChanged)

    def __onScrollValueChanged(self, value):
        """ load more online songs """
        if value != self.verticalScrollBar().maximum() or self.searchThread.isRunning():
            return

        self.searchThread.nextPage()

    def __loadMoreSongs(self, songInfos: List[SongInfo]):
        """ load more online songs """
        self.songListWidget.songInfos.extend(songInfos)
        self.songListWidget.appendSongCards(songInfos)
        self.adjustScrollHeight()
