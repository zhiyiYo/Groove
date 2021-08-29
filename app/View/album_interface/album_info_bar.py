# coding:utf-8
from components.menu import AddToMenu
from components.app_bar import (AppBarButton, CollapsingAppBarBase,
                                MoreActionsMenu)
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction


class AlbumInfoBar(CollapsingAppBarBase):

    addToPlayingPlaylistSig = pyqtSignal()
    addToNewCustomPlaylistSig = pyqtSignal()
    addToCustomPlaylistSig = pyqtSignal(str)

    def __init__(self, albumInfo: dict, parent=None):
        self.setAlbumInfo(albumInfo)
        self.playAllButton = AppBarButton(
            ":/images/album_interface/Play.png", "全部播放")
        self.addToButton = AppBarButton(
            ":/images/album_interface/Add.png", "添加到")
        self.showSingerButton = AppBarButton(
            ":/images/album_interface/Contact.png", "显示歌手")
        self.pinToStartMenuButton = AppBarButton(
            ":/images/album_interface/Pin.png", '固定到"开始"菜单')
        self.editInfoButton = AppBarButton(
            ":/images/album_interface/Edit.png", "编辑信息")
        self.deleteButton = AppBarButton(
            ":/images/album_interface/Delete.png", "删除")
        buttons = [self.playAllButton, self.addToButton, self.showSingerButton,
                   self.pinToStartMenuButton, self.editInfoButton, self.deleteButton]
        super().__init__(self.albumName,
                         f'{self.singerName}\n{self.year} • {self.genre}',
                         self.albumCoverPath, buttons, 'album', parent)

        self.actionNames = ["全部播放", "添加到", "显示歌手", '固定到"开始"菜单', "编辑信息", "删除"]
        self.action_list = [QAction(i, self) for i in self.actionNames]
        self.setAttribute(Qt.WA_StyledBackground)
        self.addToButton.clicked.connect(self.__onAddToButtonClicked)

    def setAlbumInfo(self, albumInfo: dict):
        """ 设置专辑信息 """
        self.albumInfo = albumInfo if albumInfo else {}
        self.year = albumInfo.get("year", "未知年份")  # type:str
        self.genre = albumInfo.get("genre", "未知流派")  # type:str
        self.albumName = albumInfo.get("album", "未知专辑")  # type:str
        self.singerName = albumInfo.get("singer", "未知歌手")  # type:str
        self.albumCoverPath = albumInfo.get(
            "coverPath", ":/images/default_covers/album_200_200.png")  # type:str

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
