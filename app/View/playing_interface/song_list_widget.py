# coding:utf-8
from typing import List

from common.config import Theme
from common.crawler import QueryServerType
from common.signal_bus import signalBus
from common.database.entity import SongInfo
from common.style_sheet import setStyleSheet
from components.widgets.menu import RoundMenu, AddToMenu, DownloadMenu
from components.dialog_box.song_property_dialog import SongPropertyDialog
from components.widgets.list_widget import ListWidget
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction, QApplication, QListWidgetItem

from .song_card import SongCard


class SongListWidget(ListWidget):
    """ Song list widget """

    emptyChanged = pyqtSignal(bool)                 # 歌曲列表 空/非空 变化
    removeSongSig = pyqtSignal(int)                 # 移除歌曲
    watchMvSig = pyqtSignal(SongInfo)               # 观看 MV
    currentIndexChanged = pyqtSignal(int)           # 当前播放的变化
    isAllCheckedChanged = pyqtSignal(bool)          # 歌曲卡卡全部选中改变
    selectionModeStateChanged = pyqtSignal(bool)    # 进入或退出选择模式
    checkedNumChanged = pyqtSignal(int)             # 选中的歌曲卡数量改变

    def __init__(self, songInfos: List[SongInfo], parent=None):
        super().__init__(parent)
        self.songInfos = songInfos
        self.currentIndex = 0
        self.item_list = []
        self.songCards = []  # type:List[SongCard]
        self.checkedSongCards = []  # type:List[SongCard]
        self.isInSelectionMode = False
        self.isAllSongCardsChecked = False
        self.createSongCards()
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1150 + 60, 800)
        self.setViewportMargins(30, 0, 30, 0)
        setStyleSheet(self, 'playing_interface_song_list_widget')

    def createSongCards(self):
        """ create song cards """
        for songInfo in self.songInfos:
            self.appendOneSongCard(songInfo)
            QApplication.processEvents()

        if self.songInfos:
            self.songCards[self.currentIndex].setPlay(True)

        self.resize(1200, 800)

    def resizeEvent(self, e):
        for item in self.item_list:
            item.setSizeHint(QSize(self.width() - 60, 60))

        super().resizeEvent(e)

    def __emitCurrentChangedSignal(self, index):
        """ emit current changed signal """
        self.currentIndexChanged.emit(index)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e: QContextMenuEvent):
        if self.indexAt(e.pos()).column() <= -1:
            return

        menu = SongCardContextMenu(self)
        self.__connectContextMenuSignalToSlot(menu)

        if self.currentRow() == len(self.songInfos) - 1:
            menu.moveDownAct.setEnabled(False)
        if self.currentRow() == 0:
            menu.moveUpAct.setEnabled(False)

        if self.currentSongInfo.file.startswith('http'):
            downloadMenu = DownloadMenu(self.tr('Download'), menu, Theme.DARK)
            downloadMenu.setObjectName('darkMenu')
            setStyleSheet(downloadMenu, 'menu', Theme.DARK)
            downloadMenu.downloadSig.connect(
                lambda q: signalBus.downloadSongSig.emit(self.currentSongInfo, q))
            menu.insertMenu(menu.removeAct, downloadMenu)

        menu.exec_(e.globalPos())

    def showSongPropertyDialog(self, songInfo: SongInfo = None):
        """ show song property dialog box """
        songInfo = songInfo or self.currentSongInfo
        w = SongPropertyDialog(songInfo, self.window())
        w.exec_()

    def removeSongCard(self, index):
        """ remove a song card """
        # update item index
        for songCard in self.songCards[index+1:]:
            songCard.itemIndex -= 1

        if self.currentIndex > index:
            self.currentIndex -= 1
        elif self.currentIndex == index:
            self.setCurrentIndex(index-1)

        # remove song card
        self.songInfos.pop(index)
        songCard = self.songCards.pop(index)
        songCard.deleteLater()
        self.item_list.pop(index)
        self.takeItem(index)

        self.removeSongSig.emit(index)

    def setCurrentIndex(self, index: int):
        """ set currently played song card """
        if not self.songCards or index == self.currentIndex:
            return

        self.songCards[self.currentIndex].setPlay(False)
        self.currentIndex = index
        self.songCards[index].setPlay(True)

    def setPlaylist(self, playlist: list, isResetIndex: bool = True):
        """ set playing playlist """
        self.songInfos = playlist
        self.clearSongCards(isResetIndex)
        self.createSongCards()

    def clearSongCards(self, isResetIndex: bool = True):
        """ clear song cards """
        self.item_list.clear()
        self.clear()

        for songCard in self.songCards:
            songCard.deleteLater()

        self.songCards.clear()
        self.currentIndex = 0 if isResetIndex else self.currentIndex

    def updateSongCards(self, songInfos: list, isResetIndex=True, index=0):
        """ update all song cards """
        if self.songCards:
            self.songCards[self.currentIndex].setPlay(False)

        N = len(songInfos)
        N_ = len(self.songCards)    # must use songCards to get N_

        if N > N_:
            for songInfo in songInfos[N_:]:
                self.appendOneSongCard(songInfo)
                QApplication.processEvents()
        elif N < N_:
            for i in range(N_ - 1, N - 1, -1):
                self.item_list.pop()
                songCard = self.songCards.pop()
                songCard.deleteLater()
                self.takeItem(i)
                QApplication.processEvents()

        self.songInfos = songInfos

        for i in range(min(N_, N)):
            songInfo = self.songInfos[i]
            self.songCards[i].updateSongCard(songInfo)
            QApplication.processEvents()

        self.currentIndex = index if isResetIndex else self.currentIndex
        if self.songInfos:
            self.songCards[self.currentIndex].setPlay(True)

    def updateOneSongCard(self, newSongInfo: SongInfo):
        """ update a song card """
        for i, songInfo in enumerate(self.songInfos):
            if songInfo.file == newSongInfo.file:
                self.songInfos[i] = newSongInfo
                self.songCards[i].updateSongCard(newSongInfo)

    def updateMultiSongCards(self, songInfos: List[SongInfo]):
        """ update multi song cards """
        for songInfo in songInfos:
            self.updateOneSongCard(songInfo)

    def appendOneSongCard(self, songInfo: SongInfo):
        """ append a song card """
        songCard = SongCard(songInfo, self)
        songCard.itemIndex = len(self.songCards)
        songCard.resize(self.width()-60, 60)

        item = QListWidgetItem(self)
        item.setSizeHint(QSize(songCard.width(), 60))
        self.addItem(item)
        self.setItemWidget(item, songCard)

        self.songCards.append(songCard)
        self.item_list.append(item)

        # connect song card signal to slot
        songCard.aniStartSig.connect(
            lambda: self.songCards[self.currentIndex].setPlay(False))
        songCard.clicked.connect(self.__emitCurrentChangedSignal)
        songCard.checkedStateChanged.connect(self.onCheckedStateChanged)

    def onCheckedStateChanged(self, index: int, isChecked: bool):
        """ song card checked state changed slot """
        songCard = self.songCards[index]

        if songCard not in self.checkedSongCards and isChecked:
            self.checkedSongCards.append(songCard)
        elif songCard in self.checkedSongCards and not isChecked:
            self.checkedSongCards.remove(songCard)
        else:
            return

        self.checkedNumChanged.emit(len(self.checkedSongCards))

        isAllChecked = len(self.checkedSongCards) == len(self.songCards)
        if isAllChecked != self.isAllSongCardsChecked:
            self.isAllSongCardsChecked = isAllChecked
            self.isAllCheckedChanged.emit(isAllChecked)

        if not self.isInSelectionMode:
            self.__setAllSongCardSelectionModeOpen(True)
            self.selectionModeStateChanged.emit(True)
            self.isInSelectionMode = True
        elif not self.checkedSongCards:
            self.__setAllSongCardSelectionModeOpen(False)
            self.selectionModeStateChanged.emit(False)
            self.isInSelectionMode = False

    def __setAllSongCardSelectionModeOpen(self, isOpen: bool):
        """ set whether to open selection mode """
        cursor = Qt.ArrowCursor if isOpen else Qt.PointingHandCursor
        for songCard in self.songCards:
            songCard.setSelectionModeOpen(isOpen)
            songCard.albumLabel.setCursor(cursor)
            songCard.singerLabel.setCursor(cursor)

    def setAllChecked(self, isAllChecked: bool):
        """ set checked state of all song cards """
        if self.isAllSongCardsChecked == isAllChecked:
            return

        self.isAllSongCardsChecked = isAllChecked
        for songCard in self.songCards:
            songCard.setChecked(isAllChecked)

    def unCheckAllSongCards(self):
        """ uncheck all song cards """
        for songCard in self.songCards:
            songCard.setChecked(False)

    def locateCurrentSong(self):
        """ locate current song """
        self.verticalScrollBar().setValue(60*self.currentIndex)

    @property
    def currentSongCard(self):
        return self.songCards[self.currentRow()]

    @property
    def currentSongInfo(self):
        return self.currentSongCard.songInfo

    def __connectContextMenuSignalToSlot(self, menu):
        """ connect context menu signal to slot """
        menu.playAct.triggered.connect(
            lambda: self.__emitCurrentChangedSignal(self.currentRow()))
        menu.propertyAct.triggered.connect(self.showSongPropertyDialog)
        menu.removeAct.triggered.connect(
            lambda: self.removeSongCard(self.currentRow()))
        menu.selectAct.triggered.connect(
            lambda: self.currentSongCard.setChecked(True))
        menu.showAlbumAct.triggered.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(
                self.currentSongCard.singer,
                self.currentSongCard.album
            )
        )
        menu.viewOnlineAct.triggered.connect(
            lambda: signalBus.getSongDetailsUrlSig.emit(self.currentSongInfo, QueryServerType.WANYI))
        menu.movieAct.triggered.connect(
            lambda: self.watchMvSig.emit(self.currentSongInfo))

        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, [self.currentSongInfo]))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.currentSongInfo]))


class SongCardContextMenu(RoundMenu):
    """ Song card context menu """

    def __init__(self, parent=None):
        super().__init__(parent=parent, theme=Theme.DARK)
        self.playAct = QAction(self.tr('Play'), self)
        self.addToMenu = AddToMenu(self.tr('Add to'), self, Theme.DARK)
        self.removeAct = QAction(self.tr('Remove'), self)
        self.moveUpAct = QAction(self.tr('Move up'), self)
        self.moveDownAct = QAction(self.tr('Move down'), self)
        self.showAlbumAct = QAction(self.tr('Show album'), self)
        self.propertyAct = QAction(self.tr('Properties'), self)
        self.viewOnlineAct = QAction(self.tr('View online'), self)
        self.movieAct = QAction(self.tr('Watch MV'), self)
        self.selectAct = QAction(self.tr('Select'), self)

        self.addAction(self.playAct)
        self.addMenu(self.addToMenu)
        self.addActions([
            self.removeAct, self.moveUpAct, self.moveDownAct,
            self.showAlbumAct, self.viewOnlineAct, self.movieAct,
            self.propertyAct,
        ])
        self.addSeparator()
        self.addAction(self.selectAct)

        self.setObjectName('darkMenu')
        self.addToMenu.setObjectName('darkMenu')
        setStyleSheet(self, 'menu', Theme.DARK)