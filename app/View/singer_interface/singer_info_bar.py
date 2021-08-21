# coding:utf-8
import os

from app.components.menu import AddToMenu
from app.common.image_process_utils import getBlurPixmap
from app.components.app_bar import AppBarButton, CollapsingAppBarBase, MoreActionsMenu
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPalette, QColor, QPixmap
from PyQt5.QtWidgets import QLabel, QAction


class SingerInfoBar(CollapsingAppBarBase):
    """ 歌手信息栏 """

    defaultCoverPath = 'app/resource/images/default_covers/默认歌手封面_295_295.png'

    addSongsToPlayingPlaylistSig = pyqtSignal()
    addSongsToNewCustomPlaylistSig = pyqtSignal()
    addSongsToCustomPlaylistSig = pyqtSignal(str)

    def __init__(self, singerInfo: dict, parent=None):
        self.__getInfo(singerInfo)

        # 创建按钮
        self.playAllButton = AppBarButton(
            r"app\resource\images\album_interface\Play.png", "全部播放")
        self.addToButton = AppBarButton(
            r"app\resource\images\album_interface\Add.png", "添加到")
        self.pinToStartMenuButton = AppBarButton(
            r"app\resource\images\album_interface\Pin.png", '固定到"开始"菜单')
        buttons = [self.playAllButton,
                   self.addToButton, self.pinToStartMenuButton]
        super().__init__(self.singer, self.genre, self.coverPath, buttons, 'singer', parent)

        self.blurLabel = BlurLabel(self.coverPath, 8, self)
        self.blurLabel.lower()
        self.actionNames = ["全部播放", "添加到", '固定到"开始"菜单']
        self.action_list = [QAction(i, self) for i in self.actionNames]
        self.addToButton.clicked.connect(self.__onAddToButtonClicked)
        self.blurLabel.setHidden(self.coverPath == self.defaultCoverPath)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setAutoFillBackground(True)

    def __getInfo(self, singerInfo: dict):
        """ 获取信息 """
        self.singer = singerInfo.get('singer', '未知歌手')
        self.genre = singerInfo.get('genre', '未知流派')
        self.coverPath = singerInfo.get('coverPath', "")
        self.albumInfo_list = singerInfo.get('albumInfo_list', [])
        if not os.path.exists(self.coverPath):
            self.coverPath = self.defaultCoverPath

    def setBackgroundColor(self):
        """ 根据封面背景颜色 """
        if self.coverPath == self.defaultCoverPath:
            palette = QPalette()
            palette.setColor(self.backgroundRole(), QColor(24, 24, 24))
            self.setPalette(palette)

        if hasattr(self, 'blurLabel'):
            self.blurLabel.setHidden(self.coverPath == self.defaultCoverPath)

    def updateWindow(self, singerInfo: dict):
        self.__getInfo(singerInfo)
        self.updateCover(self.coverPath)
        super().updateWindow(self.singer, self.genre, self.coverPath)

    def updateCover(self, coverPath: str):
        """ 更新封面 """
        self.coverLabel.setPixmap(QPixmap(coverPath))
        self.blurLabel.updateWindow(coverPath, 8)
        self.__adjustBlurLabel()
        self.blurLabel.show()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.__adjustBlurLabel()

    def __adjustBlurLabel(self):
        """ 调整磨砂封面 """
        w = max(self.width(), self.height())
        self.blurLabel.resize(self.width(), self.height())
        self.blurLabel.setPixmap(self.blurLabel.pixmap().scaled(
            w, w, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

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
        menu.playingAct.triggered.connect(self.addSongsToPlayingPlaylistSig)
        menu.addSongsToPlaylistSig.connect(self.addSongsToCustomPlaylistSig)
        menu.newPlaylistAct.triggered.connect(
            self.addSongsToNewCustomPlaylistSig)
        menu.exec(QPoint(x, y))



class BlurLabel(QLabel):
    """ 磨砂标签 """

    def __init__(self, imagePath: str, blurRadius=30, parent=None):
        super().__init__(parent=parent)
        self.imagePath = imagePath
        self.blurRadius = blurRadius
        self.setPixmap(getBlurPixmap(imagePath, blurRadius, 0.85))

    def updateWindow(self, imagePath: str, blurRadius=30):
        """ 更新磨砂图片 """
        self.imagePath = imagePath
        self.blurRadius = blurRadius
        self.setPixmap(getBlurPixmap(imagePath, blurRadius, 0.85))
