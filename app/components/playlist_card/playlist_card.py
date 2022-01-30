# coding:utf-8
from enum import Enum

from common.database.entity import Playlist, SongInfo
from components.widgets.menu import AddToMenu, DWMMenu
from PyQt5.QtWidgets import QAction

from .playlist_card_base import PlaylistCardBase


class PlaylistCardType(Enum):
    """ 播放列表卡类型 """
    PLAYLIST_CARD = 0
    LOCAL_SEARCHED_PLAYLIST_CARD = 1


class PlaylistCard(PlaylistCardBase):
    """ 播放列表卡 """

    def contextMenuEvent(self, e):
        """ 显示右击菜单 """
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
    """ 本地搜索得到的播放列表卡 """

    def contextMenuEvent(self, e):
        menu = LocalSearchedPlaylistCardContextMenu(self)
        menu.playAct.triggered.connect(
            lambda: self.playSig.emit(self.name))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextToPlaySig.emit(self.name))
        menu.deleteAct.triggered.connect(
            lambda: self.deleteCardSig.emit(self.name))
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
    """ 播放列表卡右击菜单 """

    def __init__(self, parent=None):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("playlistCardContextMenu")
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        # 创建动作
        self.playAct = QAction(self.tr("Play"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        self.renameAct = QAction(self.tr("Rename"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.selectAct = QAction(self.tr("Select"), self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.renameAct, self.pinToStartMenuAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)


class LocalSearchedPlaylistCardContextMenu(DWMMenu):
    """ 播放列表卡右击菜单"""

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("playlistCardContextMenu")
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        self.playAct = QAction(self.tr("Play"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        self.renameAct = QAction(self.tr("Rename"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.renameAct, self.pinToStartMenuAct, self.deleteAct])


class PlaylistCardFactory:
    """ 专辑卡工厂 """

    @staticmethod
    def create(cardType: PlaylistCardType, playlist: Playlist, parent=None) -> PlaylistCardBase:
        """ 创建播放列表卡

        Parameters
        ----------
        cardType: PlaylistCardType
            专辑卡类型

        playlist: Playlist
            播放列表

        parent:
            父级窗口

        Returns
        -------
        playlistCard:
            播放列表卡
        """
        playlistCardMap = {
            PlaylistCardType.PLAYLIST_CARD: PlaylistCard,
            PlaylistCardType.LOCAL_SEARCHED_PLAYLIST_CARD: LocalSearchedPlaylistCard,
        }

        if cardType not in playlistCardMap:
            raise ValueError("专辑卡类型非法")

        return playlistCardMap[cardType](playlist, parent)
