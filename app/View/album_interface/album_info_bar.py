# coding:utf-8
from components.widgets.menu import AddToMenu
from components.app_bar import (AppBarButton, CollapsingAppBarBase,
                                MoreActionsMenu)
from PyQt5.QtCore import QPoint, Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QAction


class AlbumInfoBar(CollapsingAppBarBase):

    addToPlayingPlaylistSig = pyqtSignal()
    addToNewCustomPlaylistSig = pyqtSignal()
    addToCustomPlaylistSig = pyqtSignal(str)

    def __init__(self, albumInfo: dict, parent=None):
        self.setAlbumInfo(albumInfo)
        super().__init__(self.albumName,
                         f'{self.singerName}\n{self.year} • {self.genre}',
                         self.albumCoverPath, 'album', parent)

        self.playAllButton = AppBarButton(
            ":/images/album_interface/Play.png", self.tr("Play all"))
        self.addToButton = AppBarButton(
            ":/images/album_interface/Add.png", self.tr("Add to"))
        self.showSingerButton = AppBarButton(
            ":/images/album_interface/Contact.png", self.tr("Show artist"))
        self.pinToStartMenuButton = AppBarButton(
            ":/images/album_interface/Pin.png", self.tr('Pin to Start'))
        self.editInfoButton = AppBarButton(
            ":/images/album_interface/Edit.png", self.tr("Edit info"))
        self.deleteButton = AppBarButton(
            ":/images/album_interface/Delete.png", self.tr("Delete"))
        self.setButtons([self.playAllButton, self.addToButton, self.showSingerButton,
                        self.pinToStartMenuButton, self.editInfoButton, self.deleteButton])

        self.actionNames = [
            self.tr("Play all"), self.tr("Add to"),
            self.tr("Show artist"), self.tr("Pin to Start"),
            self.tr("Edit info"), self.tr("Delete")
        ]
        self.action_list = [QAction(i, self) for i in self.actionNames]
        self.setAttribute(Qt.WA_StyledBackground)
        self.addToButton.clicked.connect(self.__onAddToButtonClicked)

    def setAlbumInfo(self, albumInfo: dict):
        """ 设置专辑信息 """
        obj = QObject()
        self.albumInfo = albumInfo if albumInfo else {}
        self.year = albumInfo.get("year", obj.tr("Unknown year"))
        self.genre = albumInfo.get("genre", obj.tr("Unknown genre"))
        self.albumName = albumInfo.get("album", obj.tr("Unknown album"))
        self.singerName = albumInfo.get("singer", obj.tr("Unknown artist"))
        self.albumCoverPath = albumInfo.get(
            "coverPath", ":/images/default_covers/album_200_200.png")

    def onMoreActionsButtonClicked(self):
        """ 显示更多操作菜单 """
        menu = MoreActionsMenu()
        index = len(self.buttons)-self.hiddenButtonNum
        actions = self.action_list[index:]
        menu.addActions(actions)
        pos = self.mapToGlobal(self.moreActionsButton.pos())
        x = pos.x()+self.moreActionsButton.width()+5
        y = pos.y()+self.moreActionsButton.height()//2-(13+38*len(actions))//2
        menu.exec(QPoint(x, y))

    def __onAddToButtonClicked(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        pos = self.mapToGlobal(self.addToButton.pos())
        x = pos.x() + self.addToButton.width() + 5
        y = pos.y() + self.addToButton.height() // 2 - \
            (13 + 38 * menu.actionCount()) // 2
        menu.playingAct.triggered.connect(self.addToPlayingPlaylistSig)
        menu.addSongsToPlaylistSig.connect(self.addToCustomPlaylistSig)
        menu.newPlaylistAct.triggered.connect(self.addToNewCustomPlaylistSig)
        menu.exec(QPoint(x, y))

    def updateWindow(self, albumInfo: dict):
        """ 更新窗口 """
        self.setAlbumInfo(albumInfo)
        super().updateWindow(self.albumName,
                             f'{self.singerName}\n{self.year} • {self.genre}',
                             self.albumCoverPath)
