# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from components.dialog_box.message_dialog import MessageDialog
from components.widgets.menu import AddToMenu, DWMMenu
from PyQt5.QtCore import QFile, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction, QLabel

from .no_scroll_song_list_widget import NoScrollSongListWidget
from .song_card import SongTabSongCard
from .song_card_type import SongCardType


class SongCardListContextMenu(DWMMenu):
    """ Context menu of song list widget """

    def __init__(self, parent):
        super().__init__(parent=parent)
        # create actions
        self.playAct = QAction(self.tr("Play"), self)
        self.nextSongAct = QAction(self.tr("Play next"), self)
        self.showAlbumAct = QAction(self.tr("Show album"), self)
        self.viewOnlineAct = QAction(self.tr('View online'), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.showPropertyAct = QAction(self.tr("Properties"), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.addToMenu = AddToMenu(self.tr('Add to'), self)

        # add actions to menu
        self.addActions([self.playAct, self.nextSongAct])
        self.addMenu(self.addToMenu)
        self.addActions([
            self.showAlbumAct, self.viewOnlineAct,
            self.editInfoAct, self.showPropertyAct, self.deleteAct
        ])
        self.addSeparator()
        self.addAction(self.selectAct)


class SongListWidget(NoScrollSongListWidget):
    """ Song list widget """

    playSignal = pyqtSignal(SongInfo)    # play checked song

    def __init__(self, songInfos: List[SongInfo], parent=None):
        """
        Parameters
        ----------
        songInfos: List[SongInfo]
            song information list

        parent:
            parent window
        """
        super().__init__(songInfos, SongCardType.SONG_TAB_SONG_CARD, parent)
        self.resize(1150, 758)
        self.sortMode = "Date added"
        self.sortModeMap = {
            "Date added": "createTime",
            "A to Z": "title",
            "Artist": "singer"
        }

        self.createSongCards()
        self.guideLabel = QLabel(
            self.tr("There is nothing to display here. Try a different filter."), self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__setQss()
        self.guideLabel.move(35, 40)
        self.guideLabel.setHidden(bool(self.songInfos))

    def __onPlayButtonClicked(self, index: int):
        """ play button clicked slot """
        self.playSignal.emit(self.songCards[index].songInfo)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ show context menu """
        hitIndex = self.indexAt(e.pos()).column()
        if hitIndex > -1:
            contextMenu = SongCardListContextMenu(self)
            self.__connectMenuSignalToSlot(contextMenu)
            contextMenu.exec(self.cursor().pos())

    def __onSongCardDoubleClicked(self, index: int):
        """ song card double clicked slot """
        if self.isInSelectionMode:
            return

        self.playSignal.emit(self.songCards[index].songInfo)

    def __setQss(self):
        """ set style sheet """
        self.guideLabel.setObjectName('guideLabel')
        setStyleSheet(self, 'song_list_widget')
        self.guideLabel.adjustSize()

    def setSortMode(self, sortMode: str):
        """ set sort mode of song card

        Parameters
        ----------
        sortMode: str
            sort mode, including `Date added`, `A to Z` and `Artist`
        """
        if self.sortMode == sortMode:
            return

        playingSongInfo = self.playingSongInfo
        self.sortMode = sortMode
        songInfos = self.sortSongInfo(self.sortModeMap[sortMode])
        self.updateAllSongCards(songInfos)

        if playingSongInfo in self.songInfos:
            self.setPlay(self.songInfos.index(playingSongInfo))

    def updateAllSongCards(self, songInfos: List[SongInfo]):
        self.guideLabel.setHidden(bool(songInfos))
        super().updateAllSongCards(songInfos)

    def _showDeleteCardDialog(self):
        index = self.currentRow()
        songInfo = self.songInfos[index]

        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{songInfo.title}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.removeSongCard(index))
        w.yesSignal.connect(
            lambda: self.removeSongSignal.emit(songInfo))
        w.exec_()

    def __connectMenuSignalToSlot(self, menu: SongCardListContextMenu):
        """ connect context menu signal to slot """
        menu.deleteAct.triggered.connect(self._showDeleteCardDialog)
        menu.editInfoAct.triggered.connect(self.showSongInfoEditDialog)
        menu.showPropertyAct.triggered.connect(self.showSongPropertyDialog)
        menu.playAct.triggered.connect(
            lambda: signalBus.playOneSongCardSig.emit(self.currentSongInfo))
        menu.nextSongAct.triggered.connect(
            lambda: signalBus.nextToPlaySig.emit([self.currentSongInfo]))
        menu.viewOnlineAct.triggered.connect(
            lambda: signalBus.getSongDetailsUrlSig.emit(self.currentSongInfo, 'wanyi'))
        menu.showAlbumAct.triggered.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(
                self.currentSongCard.singer,
                self.currentSongCard.album,
            )
        )
        menu.addToMenu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit([self.currentSongInfo]))
        menu.selectAct.triggered.connect(
            lambda: self.currentSongCard.setChecked(True))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, [self.currentSongInfo]))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.currentSongInfo]))

    def _connectSongCardSignalToSlot(self, songCard: SongTabSongCard):
        songCard.doubleClicked.connect(self.__onSongCardDoubleClicked)
        songCard.playButtonClicked.connect(self.__onPlayButtonClicked)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.checkedStateChanged.connect(
            self.onSongCardCheckedStateChanged)
