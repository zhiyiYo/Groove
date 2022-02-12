# coding:utf-8
from enum import Enum

from common.database.entity import AlbumInfo
from common.signal_bus import signalBus
from components.widgets.menu import AddToMenu, DWMMenu
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction

from .album_card_base import AlbumCardBase


class AlbumCardType(Enum):
    """ 歌曲卡类型枚举类 """
    ALBUM_CARD = 0
    LOCAL_SEARCHED_ALBUM_CARD = 1
    SINGER_INTERFACE_ALBUM_CARD = 2


class AlbumCard(AlbumCardBase):
    """ 专辑卡 """

    def contextMenuEvent(self, event: QContextMenuEvent):
        """ 显示右击菜单 """
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
    """ 本地搜索结果中的专辑卡 """

    def contextMenuEvent(self, event: QContextMenuEvent):
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
    """ 专辑界面专辑卡 """

    def __init__(self, albumInfo: dict, parent):
        super().__init__(albumInfo, parent)
        self.contentLabel.setText(self.year)
        self.contentLabel.setCursor(Qt.ArrowCursor)
        self.contentLabel.isSendEventToParent = True

    def updateWindow(self, newAlbumInfo: dict):
        super().updateWindow(newAlbumInfo)
        self.contentLabel.setText(self.year)

    def contextMenuEvent(self, e):
        """ 显示右击菜单 """
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
    """ 专辑卡右击菜单"""

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("albumCardContextMenu")
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        # 创建动作
        self.playAct = QAction(self.tr("Play"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.showSingerAct = QAction(self.tr("Show artist"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.showSingerAct, self.pinToStartMenuAct, self.editInfoAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)


class LocalSearchedAlbumCardContextMenu(DWMMenu):
    """ 专辑卡右击菜单"""

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("albumCardContextMenu")
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        # 创建动作
        self.playAct = QAction(self.tr("Play"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.showSingerAct = QAction(self.tr("Show artist"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.showSingerAct, self.pinToStartMenuAct])


class SingerInterfaceAlbumCardContextMenu(DWMMenu):
    """ 专辑界面专辑卡右击菜单"""

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("albumCardContextMenu")
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        # 创建动作
        self.playAct = QAction(self.tr("Play"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.pinToStartMenuAct, self.editInfoAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)


class AlbumCardFactory:
    """ 专辑卡工厂 """

    @staticmethod
    def create(cardType: AlbumCardType, albumInfo: AlbumInfo, parent=None) -> AlbumCardBase:
        """ 创建专辑卡

        Parameters
        ----------
        cardType: AlbumCardType
            专辑卡类型

        albumInfo: AlbumInfo
            专辑信息

        parent:
            父级窗口

        Returns
        -------
        albumCard:
            专辑卡
        """
        albumCardMap = {
            AlbumCardType.ALBUM_CARD: AlbumCard,
            AlbumCardType.LOCAL_SEARCHED_ALBUM_CARD: LocalSearchedAlbumCard,
            AlbumCardType.SINGER_INTERFACE_ALBUM_CARD: SingerInterfaceAlbumCard
        }

        if cardType not in albumCardMap:
            raise ValueError("专辑卡类型非法")

        return albumCardMap[cardType](albumInfo, parent)
