# coding:utf-8
from enum import Enum

from common.database.entity import AlbumInfo
from common.signal_bus import signalBus
from components.widgets.menu import AddToMenu, DWMMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction

from .album_card_base import AlbumCardBase


class AlbumCardType(Enum):
    """ Album card type enumerated class """
    ALBUM_CARD = 0
    LOCAL_SEARCHED_ALBUM_CARD = 1
    SINGER_INTERFACE_ALBUM_CARD = 2


class AlbumCard(AlbumCardBase):
    """ Album card """

    def contextMenuEvent(self, event: QContextMenuEvent):
        super().contextMenuEvent(event)
        menu = AlbumCardContextMenu(parent=self)
        menu.playAct.triggered.connect(
            lambda: signalBus.playAlbumSig.emit(self.singer, self.album))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.singer, self.album))
        menu.deleteAct.triggered.connect(
            lambda: self.deleteCardSig.emit(self.singer, self.album))
        menu.editInfoAct.triggered.connect(self.showAlbumInfoEditDialog)
        menu.selectAct.triggered.connect(self._onSelectActionTriggered)
        menu.showSingerAct.triggered.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))

        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.singer, self.album))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addAlbumToCustomPlaylistSig.emit(name, self.singer, self.album))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addAlbumToNewCustomPlaylistSig.emit(self.singer, self.album))

        menu.exec(event.globalPos())


class LocalSearchedAlbumCard(AlbumCardBase):
    """ Album card in local search result """

    def contextMenuEvent(self, event: QContextMenuEvent):
        super().contextMenuEvent(event)
        menu = LocalSearchedAlbumCardContextMenu(parent=self)
        menu.playAct.triggered.connect(
            lambda: signalBus.playAlbumSig.emit(self.singer, self.album))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.singer, self.album))
        menu.showSingerAct.triggered.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))

        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.singer, self.album))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addAlbumToCustomPlaylistSig.emit(name, self.singer, self.album))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addAlbumToNewCustomPlaylistSig.emit(self.singer, self.album))
        menu.exec(event.globalPos())


class SingerInterfaceAlbumCard(AlbumCardBase):
    """ Album card in singer interface """

    def __init__(self, albumInfo: dict, parent):
        super().__init__(albumInfo, parent)
        self.contentLabel.setText(self.year)
        self.contentLabel.setCursor(Qt.ArrowCursor)
        self.contentLabel.isSendEventToParent = True

    def updateWindow(self, newAlbumInfo: dict):
        super().updateWindow(newAlbumInfo)
        self.contentLabel.setText(self.year)

    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        menu = SingerInterfaceAlbumCardContextMenu(parent=self)
        menu.playAct.triggered.connect(
            lambda: signalBus.playAlbumSig.emit(self.singer, self.album))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.singer, self.album))
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.singer, self.album))
        menu.editInfoAct.triggered.connect(self.showAlbumInfoEditDialog)
        menu.selectAct.triggered.connect(self._onSelectActionTriggered)
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addAlbumToCustomPlaylistSig.emit(name, self.singer, self.album))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addAlbumToNewCustomPlaylistSig.emit(self.singer, self.album))
        menu.deleteAct.triggered.connect(
            lambda: self.deleteCardSig.emit(self.album))
        menu.exec(e.globalPos())


class AlbumCardContextMenu(DWMMenu):
    """ Context menu of album card """

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("albumCardContextMenu")
        self.setQss()

    def __createActions(self):
        # create actions
        self.playAct = QAction(self.tr("Play"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.showSingerAct = QAction(self.tr("Show artist"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        # add actions to menu
        self.addActions([self.playAct, self.nextToPlayAct])
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.showSingerAct, self.pinToStartMenuAct, self.editInfoAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)


class LocalSearchedAlbumCardContextMenu(DWMMenu):
    """ Context menu of local searched album card """

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("albumCardContextMenu")
        self.setQss()

    def __createActions(self):
        # create actions
        self.playAct = QAction(self.tr("Play"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.showSingerAct = QAction(self.tr("Show artist"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        # add actions to menu
        self.addActions([self.playAct, self.nextToPlayAct])
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.showSingerAct, self.pinToStartMenuAct])


class SingerInterfaceAlbumCardContextMenu(DWMMenu):
    """ Context menu of singer interface album card"""

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("albumCardContextMenu")
        self.setQss()

    def __createActions(self):
        # create actions
        self.playAct = QAction(self.tr("Play"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        # add actions to menu
        self.addActions([self.playAct, self.nextToPlayAct])
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.pinToStartMenuAct, self.editInfoAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)


class AlbumCardFactory:
    """ Album card factory """

    @staticmethod
    def create(cardType: AlbumCardType, albumInfo: AlbumInfo, parent=None) -> AlbumCardBase:
        """ create an album card

        Parameters
        ----------
        cardType: AlbumCardType
            album card type

        albumInfo: AlbumInfo
            album information

        parent:
            parent window

        Returns
        -------
        albumCard:
            album card
        """
        albumCardMap = {
            AlbumCardType.ALBUM_CARD: AlbumCard,
            AlbumCardType.LOCAL_SEARCHED_ALBUM_CARD: LocalSearchedAlbumCard,
            AlbumCardType.SINGER_INTERFACE_ALBUM_CARD: SingerInterfaceAlbumCard
        }

        if cardType not in albumCardMap:
            raise ValueError(f"Album card type `{cardType}` is illegal")

        return albumCardMap[cardType](albumInfo, parent)
