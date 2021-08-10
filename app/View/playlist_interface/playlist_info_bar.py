# coding:utf-8
from math import ceil

from app.common.get_cover_path import getCoverPath
from app.components.menu import AddToMenu
from app.components.app_bar import (AppBarButton, CollapsingAppBarBase,
                                    MoreActionsMenu)
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction


class PlaylistInfoBar(CollapsingAppBarBase):

    addToPlayingPlaylistSig = pyqtSignal()
    addToNewCustomPlaylistSig = pyqtSignal()
    addToCustomPlaylistSig = pyqtSignal(str)

    def __init__(self, playlist: dict, parent=None):
        self.__getPlaylistInfo(playlist)
        self.playAllButton = AppBarButton(
            r"app\resource\images\album_interface\Play.png", "全部播放")
        self.addToButton = AppBarButton(
            r"app\resource\images\album_interface\Add.png", "添加到")
        self.renameButton = AppBarButton(
            r"app\resource\images\album_interface\Edit.png", "重命名")
        self.pinToStartMenuButton = AppBarButton(
            r"app\resource\images\album_interface\Pin.png", '固定到"开始"菜单')
        self.deleteButton = AppBarButton(
            r"app\resource\images\album_interface\Delete.png", "删除")
        buttons = [self.playAllButton, self.addToButton, self.renameButton,
                   self.pinToStartMenuButton, self.deleteButton]
        super().__init__(self.playlistName,
                         f'{len(self.songInfo_list)} 首歌曲 • {self.duration}',
                         self.playlistCoverPath, buttons, True, parent)
        self.actionNames = ["全部播放", "添加到", "重命名", '固定到"开始"菜单', "删除"]
        self.action_list = [QAction(i, self) for i in self.actionNames]
        self.setAttribute(Qt.WA_StyledBackground)
        self.addToButton.clicked.connect(self.__onAddToButtonClicked)

    def __getPlaylistInfo(self, playlist: dict):
        """ 设置专辑信息 """
        self.playlist = playlist if playlist else {}
        self.playlistName = playlist.get("playlistName", "未知播放列表")  # type:str
        self.songInfo_list = self.playlist.get("songInfo_list", [])
        songInfo = self.songInfo_list[0] if self.songInfo_list else {}
        self.playlistCoverPath = getCoverPath(
            songInfo.get("modifiedAlbum"), "playlist_big")

        # 统计时间
        seconds = 0
        for songInfo in self.songInfo_list:
            m, s = map(int, songInfo.get("duration", "0:00").split(':'))
            seconds += m*60+s
        self.hours = seconds//3600
        self.minutes = ceil((seconds % 3600)/60)
        self.duration = f"{self.hours} 小时 {self.minutes} 分钟" if self.hours > 0 else f"{self.minutes} 分钟"

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
        super().updateWindow(self.playlistName,
                             f'{len(self.songInfo_list)} 首歌曲 • {self.duration}',
                             self.playlistCoverPath)

    def setBackgroundColor(self):
        """ 根据封面背景颜色 """
        path = "app/resource/images/default_covers/默认播放列表封面_275_275.png"
        if self.playlistCoverPath != path:
            super().setBackgroundColor()
        else:
            self.setStyleSheet("background:rgb(24,24,24)")
