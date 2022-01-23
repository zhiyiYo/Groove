# coding:utf-8
from math import ceil

from common.os_utils import getCoverPath
from components.widgets.menu import AddToMenu
from components.app_bar import (AppBarButton, CollapsingAppBarBase,
                                MoreActionsMenu)
from PyQt5.QtCore import QPoint, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QAction


class PlaylistInfoBar(CollapsingAppBarBase):

    addToPlayingPlaylistSig = pyqtSignal()
    addToNewCustomPlaylistSig = pyqtSignal()
    addToCustomPlaylistSig = pyqtSignal(str)

    def __init__(self, playlist: dict, parent=None):
        self.__getPlaylistInfo(playlist)
        content = str(len(self.songInfos)) + \
            QObject().tr(" songs")+f' • {self.duration}'
        super().__init__(self.playlistName, content,
                         self.playlistCoverPath, 'playlist', parent)

        self.playAllButton = AppBarButton(
            ":/images/album_interface/Play.png", self.tr("Play all"))
        self.addToButton = AppBarButton(
            ":/images/album_interface/Add.png", self.tr("Add to"))
        self.renameButton = AppBarButton(
            ":/images/album_interface/Edit.png", self.tr("Rename"))
        self.pinToStartMenuButton = AppBarButton(
            ":/images/album_interface/Pin.png", self.tr('Pin to Start'))
        self.deleteButton = AppBarButton(
            ":/images/album_interface/Delete.png", self.tr("Delete"))

        self.setButtons([self.playAllButton, self.addToButton, self.renameButton,
                         self.pinToStartMenuButton, self.deleteButton])

        self.actionNames = [
            self.tr("Play all"), self.tr("Add to"),
            self.tr("Rename"), self.tr('Pin to Start'), self.tr("Delete")]
        self.action_list = [QAction(i, self) for i in self.actionNames]
        self.setAttribute(Qt.WA_StyledBackground)
        self.addToButton.clicked.connect(self.__onAddToButtonClicked)

    def __getPlaylistInfo(self, playlist: dict):
        """ 设置专辑信息 """
        obj = QObject()
        self.playlist = playlist if playlist else {}
        self.playlistName = playlist.get(
            "playlistName", obj.tr("Unknown playlist"))

        self.songInfos = self.playlist.get("songInfos", [])
        songInfo = self.songInfos[0] if self.songInfos else {}
        name = songInfo.get('coverName', '未知歌手_未知专辑')
        self.playlistCoverPath = getCoverPath(name, "playlist_big")

        # 统计时间
        seconds = 0
        for songInfo in self.songInfos:
            m, s = map(int, songInfo.get("duration", "0:00").split(':'))
            seconds += m*60+s
        self.hours = seconds//3600
        self.minutes = ceil((seconds % 3600)/60)
        h = obj.tr('hrs')
        m = obj.tr('mins')
        self.duration = f"{self.hours} {h} {self.minutes} {m}" if self.hours > 0 else f"{self.minutes} {m}"

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

    def updateWindow(self, playlist: dict):
        """ 更新窗口 """
        self.__getPlaylistInfo(playlist)
        content = str(len(self.songInfos)) + \
            self.tr(" songs")+f' • {self.duration}'
        super().updateWindow(self.playlistName, content, self.playlistCoverPath)

    def setBackgroundColor(self):
        """ 根据封面背景颜色 """
        path = ":/images/default_covers/playlist_113_113.png"
        if self.playlistCoverPath != path:
            super().setBackgroundColor()
        else:
            palette = QPalette()
            palette.setColor(self.backgroundRole(), QColor(24, 24, 24))
            self.setPalette(palette)
