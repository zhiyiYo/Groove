# coding: utf-8
from enum import Enum

from common.database.entity import SingerInfo
from common.signal_bus import signalBus
from components.widgets.menu import AddToMenu, DWMMenu
from PyQt5.QtWidgets import QAction

from .singer_card_base import SingerCardBase


class SingerCardType(Enum):
    """ Singer card type enumerated class """
    SINGER_CARD = 0
    LOCAL_SEARCHED_SINGER_CARD = 1


class SingerCard(SingerCardBase):
    """ Singer card """

    def contextMenuEvent(self, event):
        menu = SingerCardContextMenu(parent=self)
        menu.playAct.triggered.connect(lambda: self.playSignal.emit(self.singer))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.singer))
        menu.selectAct.triggered.connect(self._onSelectActionTriggered)

        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.singer))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSingerToCustomPlaylistSig.emit(name, self.singer))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSingerToNewCustomPlaylistSig.emit(self.singer))

        menu.exec(event.globalPos())


class LocalSearchedSingerCard(SingerCardBase):
    """ Singer card in local search result """

    def contextMenuEvent(self, event):
        menu = LocalSearchedSingerCardContextMenu(parent=self)
        menu.playAct.triggered.connect(lambda: self.playSignal.emit(self.singer))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.singer))

        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.singer))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSingerToCustomPlaylistSig.emit(name, self.singer))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSingerToNewCustomPlaylistSig.emit(self.singer))
        menu.exec(event.globalPos())


class SingerCardContextMenu(DWMMenu):
    """ Context menu of album card """

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("singerCardContextMenu")
        self.setQss()

    def __createActions(self):
        # create actions
        self.playAct = QAction(self.tr("Play"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        # add actions to menu
        self.addActions([self.playAct, self.nextToPlayAct])
        self.addMenu(self.addToMenu)
        self.addAction(self.pinToStartMenuAct)
        self.addSeparator()
        self.addAction(self.selectAct)


class LocalSearchedSingerCardContextMenu(DWMMenu):
    """ Context menu of local searched singer card """

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("singerCardContextMenu")
        self.setQss()

    def __createActions(self):
        # create actions
        self.playAct = QAction(self.tr("Play"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        # add actions to menu
        self.addActions([self.playAct, self.nextToPlayAct])
        self.addMenu(self.addToMenu)
        self.addAction(self.pinToStartMenuAct)


class SingerCardFactory:
    """ Album card factory """

    @staticmethod
    def create(cardType: SingerCardType, singerInfo: SingerInfo, parent=None) -> SingerCardBase:
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
        singerCardMap = {
            SingerCardType.SINGER_CARD: SingerCard,
            SingerCardType.LOCAL_SEARCHED_SINGER_CARD: LocalSearchedSingerCard,
        }

        if cardType not in singerCardMap:
            raise ValueError(f"Album card type `{cardType}` is illegal")

        return singerCardMap[cardType](singerInfo, parent)
