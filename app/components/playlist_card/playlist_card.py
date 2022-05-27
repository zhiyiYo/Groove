# coding:utf-8
from enum import Enum

from common.database.entity import Playlist, SongInfo
from common.signal_bus import signalBus
from components.widgets.menu import AddToMenu, DWMMenu
from PyQt5.QtWidgets import QAction

from .playlist_card_base import PlaylistCardBase


class PlaylistCardType(Enum):
    """ Playlist card type """
    PLAYLIST_CARD = 0
    LOCAL_SEARCHED_PLAYLIST_CARD = 1


class PlaylistCard(PlaylistCardBase):
    """ Playlist card """

    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        menu = PlaylistCardContextMenu(parent=self)

        menu.playAct.triggered.connect(lambda: self.playSig.emit(self.name))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextToPlaySig.emit(self.name))
        menu.deleteAct.triggered.connect(
            lambda: self.deleteCardSig.emit(self.name))
        menu.renameAct.triggered.connect(
            lambda: self.renamePlaylistSig.emit(self.name))
        menu.selectAct.triggered.connect(self._onSelectActionTrigerred)
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(self.name))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(self.name))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.name))

        menu.exec(e.globalPos())


class LocalSearchedPlaylistCard(PlaylistCardBase):
    """ Playlist card in local search result """

    def contextMenuEvent(self, e):
        super().contextMenuEvent(e)
        menu = LocalSearchedPlaylistCardContextMenu(self)
        menu.playAct.triggered.connect(
            lambda: self.playSig.emit(self.name))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextToPlaySig.emit(self.name))
        menu.renameAct.triggered.connect(
            lambda: self.renamePlaylistSig.emit(self.name))
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(self.name))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(self.name))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.name))
        menu.exec(e.globalPos())


class PlaylistCardContextMenu(DWMMenu):
    """ Context menu of playlist card """

    def __init__(self, parent=None):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("playlistCardContextMenu")
        self.setQss()

    def __createActions(self):
        # create actions
        self.playAct = QAction(self.tr("Play"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        self.renameAct = QAction(self.tr("Rename"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.selectAct = QAction(self.tr("Select"), self)

        # add actions to menu
        self.addActions([self.playAct, self.nextToPlayAct])
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.renameAct, self.pinToStartMenuAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)


class LocalSearchedPlaylistCardContextMenu(DWMMenu):
    """ Context menu of local searched playlist card"""

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("playlistCardContextMenu")
        self.setQss()

    def __createActions(self):
        # create actions
        self.playAct = QAction(self.tr("Play"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        self.renameAct = QAction(self.tr("Rename"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)

        # add actions to menu
        self.addActions([self.playAct, self.nextToPlayAct])
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.renameAct, self.pinToStartMenuAct])


class PlaylistCardFactory:
    """ Playlist card factory """

    @staticmethod
    def create(cardType: PlaylistCardType, playlist: Playlist, parent=None) -> PlaylistCardBase:
        """ create a playlist card

        Parameters
        ----------
        cardType: PlaylistCardType
            playlist card type

        playlist: Playlist
            custom playlist

        parent:
            parent window

        Returns
        -------
        playlistCard:
            playlist card
        """
        playlistCardMap = {
            PlaylistCardType.PLAYLIST_CARD: PlaylistCard,
            PlaylistCardType.LOCAL_SEARCHED_PLAYLIST_CARD: LocalSearchedPlaylistCard,
        }

        if cardType not in playlistCardMap:
            raise ValueError(f"Playlist card type `{cardType}` is illegal")

        return playlistCardMap[cardType](playlist, parent)
