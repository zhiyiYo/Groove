# coding:utf-8
from typing import List

from common.crawler import QueryServerType
from common.database.entity import SongInfo
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from components.dialog_box.message_dialog import MessageDialog
from components.song_list_widget import NoScrollSongListWidget, SongCardType
from components.song_list_widget.song_card import AlbumInterfaceSongCard
from components.widgets.menu import AddToMenu, RoundMenu
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction


class SongCardListContextMenu(RoundMenu):
    """ Context menu of song list widget """

    def __init__(self, parent):
        super().__init__("", parent)
        self.playAct = QAction(self.tr("Play"), self)
        self.nextSongAct = QAction(self.tr("Play next"), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.viewOnlineAct = QAction(self.tr('View online'), self)
        self.showPropertyAct = QAction(self.tr("Properties"), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        self.addActions([self.playAct, self.nextSongAct])
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.viewOnlineAct, self.editInfoAct, self.showPropertyAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)


class SongListWidget(NoScrollSongListWidget):
    """ Song list widget of album interface """

    playSignal = pyqtSignal(int)   # 播放指定歌曲

    def __init__(self, songInfos: List[SongInfo], parent=None):
        """
        Parameters
        ----------
        songInfos: List[SongInfo]
            song information list

        parent:
            parent window
        """
        super().__init__(songInfos, SongCardType.ALBUM_INTERFACE_SONG_CARD, parent)
        self.createSongCards()
        setStyleSheet(self, 'song_list_widget')

    def __showMaskDialog(self):
        index = self.currentRow()
        name = self.songInfos[index]['songName']
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{name}" ' + \
            self.tr("it won't be on be this device anymore.")
        w = MessageDialog(title, content, self.window())
        if w.exec_():
            self.removeSongCard(index)

    def contextMenuEvent(self, e: QContextMenuEvent):
        hitIndex = self.indexAt(e.pos()).column()
        if hitIndex > -1:
            contextMenu = SongCardListContextMenu(self)
            self.__connectMenuSignalToSlot(contextMenu)
            contextMenu.exec(self.cursor().pos())

    def __onSongCardDoubleClicked(self, index):
        """ song card double clicked slot """
        if self.isInSelectionMode:
            return

        self.playSignal.emit(index)

    def __connectMenuSignalToSlot(self, menu: SongCardListContextMenu):
        """ connect context menu signal to slot """
        menu.deleteAct.triggered.connect(self.__showMaskDialog)
        menu.editInfoAct.triggered.connect(self.showSongInfoEditDialog)
        menu.showPropertyAct.triggered.connect(self.showSongPropertyDialog)
        menu.playAct.triggered.connect(
            lambda: signalBus.playOneSongCardSig.emit(self.currentSongInfo))
        menu.nextSongAct.triggered.connect(
            lambda: signalBus.nextToPlaySig.emit([self.currentSongInfo]))
        menu.viewOnlineAct.triggered.connect(
            lambda: signalBus.getSongDetailsUrlSig.emit(self.currentSongInfo, QueryServerType.WANYI))
        menu.addToMenu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit([self.currentSongInfo]))
        menu.selectAct.triggered.connect(
            lambda: self.currentSongCard.setChecked(True))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, self.songInfos))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.currentSongInfo]))

    def _connectSongCardSignalToSlot(self, songCard: AlbumInterfaceSongCard):
        """ connect song card signal to slot """
        songCard.doubleClicked.connect(self.__onSongCardDoubleClicked)
        songCard.playButtonClicked.connect(self.playSignal)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.checkedStateChanged.connect(
            self.onSongCardCheckedStateChanged)
