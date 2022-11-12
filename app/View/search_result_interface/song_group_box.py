# coding:utf-8
from typing import List

from common.crawler import QueryServerType
from common.database.entity import SongInfo
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from components.buttons.three_state_button import ThreeStatePushButton
from components.song_list_widget import NoScrollSongListWidget, SongCardType
from components.song_list_widget.song_card import (NoCheckBoxSongCard,
                                                   OnlineSongCard)
from components.widgets.label import ClickableLabel
from components.widgets.menu import AddToMenu, DownloadMenu, DWMMenu
from PyQt5.QtCore import QFile, QMargins, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction, QPushButton, QWidget


class SongGroupBox(QWidget):
    """ Song group box """

    loadMoreSignal = pyqtSignal()
    switchToMoreSearchResultInterfaceSig = pyqtSignal()

    def __init__(self, song_type: str, parent=None):
        """
        Parameters
        ----------
        song_type: str
            song type, could be `'Online songs'` or `'Local songs'`

        parent:
            parent window
        """
        super().__init__(parent=parent)
        if song_type not in ['Online songs', 'Local songs']:
            raise ValueError(
                "Song type must be 'Online songs' or 'Local songs'")

        self.songType = song_type
        self.isOnline = song_type == 'Online songs'
        self.songInfos = []
        if not self.isOnline:
            self.songListWidget = LocalSongListWidget(self)
            self.titleButton = QPushButton(self.tr('Local songs'), self)
            self.loadMoreLabel = ClickableLabel()
            self.loadMoreLabel.hide()   # 隐藏本地歌曲的加载更多标签
        else:
            self.songListWidget = OnlineSongListWidget(self)
            self.titleButton = QPushButton(self.tr('Online songs'), self)
            self.loadMoreLabel = ClickableLabel(self.tr("Load more"), self)

        self.showAllButton = ThreeStatePushButton(
            {
                "normal": ":/images/search_result_interface/ShowAll_normal.png",
                "hover": ":/images/search_result_interface/ShowAll_hover.png",
                "pressed": ":/images/search_result_interface/ShowAll_pressed.png",
            },
            self.tr(' Show All'),
            (14, 14),
            self,
        )
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1200, 500)
        self.setMinimumHeight(47)
        self.titleButton.move(35, 0)
        self.songListWidget.move(0, 57)
        self.loadMoreLabel.setCursor(Qt.PointingHandCursor)
        self.showAllButton.setHidden(self.isOnline)
        self.titleButton.clicked.connect(self.__showMoreSearchResultInterface)
        self.showAllButton.clicked.connect(
            self.__showMoreSearchResultInterface)
        self.loadMoreLabel.clicked.connect(self.__onLoadMoreLabelClicked)
        self.__setQss()

    def __setQss(self):
        """ set style sheet """
        self.titleButton.setObjectName('titleButton')
        self.showAllButton.setObjectName('showAllButton')
        self.loadMoreLabel.setProperty("loadFinished", "false")
        setStyleSheet(self, 'song_group_box')
        self.titleButton.adjustSize()
        self.showAllButton.adjustSize()

    def resizeEvent(self, e):
        self.songListWidget.resize(self.width(), self.songListWidget.height())
        self.showAllButton.move(self.width()-self.showAllButton.width()-30, 5)
        self.loadMoreLabel.move(self.width()//2-self.loadMoreLabel.width()//2,
                                57+self.songListWidget.height()+17)

    def __adjustHeight(self):
        spacing = 0 if not self.isOnline else 17*2+19
        self.setFixedHeight(57+self.songListWidget.height()+spacing)
        self.loadMoreLabel.move(self.loadMoreLabel.x(),
                                57+self.songListWidget.height()+17)

    def updateWindow(self, songInfos: List[SongInfo]):
        """ update window """
        if songInfos == self.songInfos:
            return

        self.songInfos = songInfos
        self.songListWidget.updateAllSongCards(self.songInfos)
        self.__adjustHeight()

    def loadMoreOnlineMusic(self, songInfos: List[SongInfo]):
        """ load more online music

        Parameters
        ----------
        songInfos: List[SongInfo]
            newly added song information list
        """
        if self.songType != 'Online songs':
            return

        self.loadMoreLabel.hide()
        self.songInfos.extend(songInfos)
        self.songListWidget.songInfos = self.songInfos
        self.songListWidget.appendSongCards(songInfos)
        self.__adjustHeight()
        self.loadMoreLabel.show()

    def __onLoadMoreLabelClicked(self):
        """ load more """
        if self.loadMoreLabel.isHidden() or self.loadMoreLabel.property("loadFinished") == "true":
            return

        self.loadMoreSignal.emit()

    def __showMoreSearchResultInterface(self):
        """ show more search result interface """
        if self.songType == 'Online songs':
            return

        self.switchToMoreSearchResultInterfaceSig.emit()


class LocalSongListWidget(NoScrollSongListWidget):
    """ Local song list widget """

    playSignal = pyqtSignal(int)     # 将播放列表的当前歌曲切换为指定的歌曲卡

    def __init__(self, parent=None):
        super().__init__(None, SongCardType.NO_CHECKBOX_SONG_CARD,
                         parent, QMargins(30, 0, 30, 0), 0)
        setStyleSheet(self, 'song_list_widget')

    def contextMenuEvent(self, e):
        hitIndex = self.indexAt(e.pos()).column()
        if hitIndex > -1:
            contextMenu = LocalSongListContextMenu(self)
            self.__connectContextMenuSignalToSlot(contextMenu)
            contextMenu.exec(self.cursor().pos())

    def __connectContextMenuSignalToSlot(self, menu):
        menu.playAct.triggered.connect(
            lambda: signalBus.playOneSongCardSig.emit(self.currentSongInfo))
        menu.nextSongAct.triggered.connect(
            lambda: signalBus.nextToPlaySig.emit([self.currentSongInfo]))
        menu.viewOnlineAct.triggered.connect(
            lambda: signalBus.getSongDetailsUrlSig.emit(self.currentSongInfo, QueryServerType.WANYI))
        menu.showPropertyAct.triggered.connect(self.showSongPropertyDialog)
        menu.showAlbumAct.triggered.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(
                self.currentSongCard.singer,
                self.currentSongCard.album
            )
        )

        menu.addToMenu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit([self.currentSongInfo]))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, [self.currentSongInfo]))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.currentSongInfo]))

    def _connectSongCardSignalToSlot(self, songCard: NoCheckBoxSongCard):
        songCard.doubleClicked.connect(self.playSignal)
        songCard.playButtonClicked.connect(self.playSignal)
        songCard.clicked.connect(self.setCurrentIndex)


class OnlineSongListWidget(NoScrollSongListWidget):
    """ Online song list widget """

    playSignal = pyqtSignal(int)    # 将播放列表的当前歌曲切换为指定的歌曲卡

    def __init__(self, parent=None):
        super().__init__(None, SongCardType.ONLINE_SONG_CARD,
                         parent, QMargins(30, 0, 30, 0), 0)
        setStyleSheet(self, 'song_list_widget')

    def contextMenuEvent(self, e):
        hitIndex = self.indexAt(e.pos()).column()
        if hitIndex > -1:
            menu = OnlineSongListContextMenu(self)
            self.__connectContextMenuSignalToSlot(menu)
            menu.exec(self.cursor().pos())

    def _connectSongCardSignalToSlot(self, songCard: OnlineSongCard):
        songCard.doubleClicked.connect(self.playSignal)
        songCard.playButtonClicked.connect(self.playSignal)
        songCard.clicked.connect(self.setCurrentIndex)

    def __connectContextMenuSignalToSlot(self, menu):
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
        menu.addToMenu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit([self.currentSongInfo]))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, [self.currentSongInfo]))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.currentSongInfo]))


class LocalSongListContextMenu(DWMMenu):
    """ Local song list widget context menu """

    def __init__(self, parent):
        super().__init__("", parent)
        self.playAct = QAction(self.tr("Play"), self)
        self.nextSongAct = QAction(self.tr("Play next"), self)
        self.showAlbumAct = QAction(self.tr("Show album"), self)
        self.viewOnlineAct = QAction(self.tr('View online'), self)
        self.showPropertyAct = QAction(self.tr("Properties"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        self.addActions([self.playAct, self.nextSongAct])
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.showAlbumAct, self.viewOnlineAct, self.showPropertyAct])


class OnlineSongListContextMenu(DWMMenu):
    """ Online song list widget context menu """

    def __init__(self, parent):
        super().__init__("", parent)
        self.setObjectName('onlineSongListContextMenu')
        self.playAct = QAction(self.tr("Play"), self)
        self.nextSongAct = QAction(self.tr("Play next"), self)
        self.viewOnlineAct = QAction(self.tr('View online'), self)
        self.showPropertyAct = QAction(self.tr("Properties"), self)
        self.downloadMenu = DownloadMenu(self.tr('Download'), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        self.addActions([self.playAct, self.nextSongAct])
        self.addMenu(self.addToMenu)
        self.addAction(self.viewOnlineAct)
        self.addMenu(self.downloadMenu)
        self.addAction(self.showPropertyAct)
