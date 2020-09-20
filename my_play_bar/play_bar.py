# coding:utf-8

from ctypes.wintypes import HWND

from PyQt5.QtCore import QEvent, QPoint, QRect, Qt
from PyQt5.QtWidgets import QWidget

from effects.window_effect import WindowEffect
from my_functions.get_dominant_color import DominantColor
from my_play_bar.central_button_group import CentralButtonGroup
from my_play_bar.more_actions_menu import MoreActionsMenu
from my_play_bar.play_progress_bar import PlayProgressBar
from my_play_bar.right_widget_group import RightWidgetGroup
from my_play_bar.song_info_card import SongInfoCard


class PlayBar(QWidget):
    """ 底部播放栏 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.originWidth = 1280
        # 实例化窗口特效
        self.windowEffect = WindowEffect()
        self.hWnd = HWND(int(self.winId()))
        self.acrylicColor = '356c8aCC'
        self.dominantColor = DominantColor()
        # 记录移动次数
        self.moveTime = 0
        self.resizeTime = 0
        # 实例化小部件
        self.playProgressBar = PlayProgressBar(
            songInfo.get('duration', '0:00'), self)
        self.songInfoCard = SongInfoCard(songInfo, self)
        self.centralButtonGroup = CentralButtonGroup(self)
        self.rightWidgetGroup = RightWidgetGroup(self)
        self.moreActionsMenu = MoreActionsMenu(self)
        # 初始化小部件
        self.__initWidget()
        self.__setQss()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.resize(1312, 115)
        self.setFixedHeight(115)
        # 初始化亚克力背景色
        self.setAcrylicColor(self.acrylicColor)
        # 引用小部件
        self.referenceWidgets()
        # 连接槽函数
        self.songInfoCard.albumChanged.connect(self.updateDominantColor)
        self.moreActionsButton.clicked.connect(self.showMoreActionsMenu)
        # 设置小部件位置
        self.__setWidgetPos()

    def __setWidgetPos(self):
        """ 初始化布局 """
        self.playProgressBar.move(
            int(self.width() / 2 - self.playProgressBar.width() / 2), self.centralButtonGroup.height())
        self.centralButtonGroup.move(
            int(self.width()/2-self.centralButtonGroup.width()/2), 0)
        self.rightWidgetGroup.move(
            self.width() - self.rightWidgetGroup.width(), 0)

    def updateDominantColor(self, albumPath: str):
        """ 更新主色调 """
        self.acrylicColor = self.dominantColor.getDominantColor(
            albumPath) + 'CC'
        self.setAcrylicColor(self.acrylicColor)

    def setAcrylicColor(self, gradientColor: str):
        """ 设置亚克力效果的混合色 """
        self.windowEffect.setAcrylicEffect(self.hWnd, gradientColor)

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\playBar.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 调整歌曲信息卡宽度 """
        deltaWidth = self.width() - self.originWidth
        # 调整进度条的宽度
        self.playProgressBar.resize(self.playProgressBar.width(
        ) + int(deltaWidth / 3), self.playProgressBar.height())
        # 调整歌曲信息卡宽度和部件位置
        if deltaWidth < 0:
            self.__setWidgetPos()
            self.__adjustSongInfoCardWidth()
        elif deltaWidth > 0:
            if self.playProgressBar.x() <= self.songInfoCard.width() + 20 or self.songInfoCard.scrollTextWindow.maxWidth != 250:
                self.__setWidgetPos()
                if deltaWidth + self.songInfoCard.width() >= self.songInfoCard.MAXWIDTH:
                    self.songInfoCard.setFixedWidth(
                        min(self.songInfoCard.MAXWIDTH, self.playProgressBar.x()-20))
                else:
                    self.songInfoCard.setFixedWidth(
                        min(self.songInfoCard.width() + deltaWidth, self.playProgressBar.x() - 20))
                self.songInfoCard.scrollTextWindow.maxWidth = self.songInfoCard.width() - 155
                self.songInfoCard.scrollTextWindow.initFlagsWidth()
            else:
                self.__setWidgetPos()
        self.originWidth = self.width()

    def showMoreActionsMenu(self):
        """ 显示更多操作菜单 """
        globalPos = self.rightWidgetGroup.mapToGlobal(
            self.moreActionsButton.pos())
        x = globalPos.x() + self.moreActionsButton.width() + 30
        y = int(globalPos.y() + self.moreActionsButton.height() /
                2 - 152 / 2)
        self.moreActionsMenu.exec(QPoint(x, y))

    def referenceWidgets(self):
        """ 引用小部件及其方法 """
        self.randomPlayButton = self.centralButtonGroup.randomPlayButton
        self.lastSongButton = self.centralButtonGroup.lastSongButton
        self.playButton = self.centralButtonGroup.playButton
        self.nextSongButton = self.centralButtonGroup.nextSongButton
        self.loopModeButton = self.centralButtonGroup.loopModeButton
        self.progressSlider = self.playProgressBar.progressSlider
        self.volumeButton = self.rightWidgetGroup.volumeButton
        self.volumeSlider = self.rightWidgetGroup.volumeSlider
        self.smallPlayModeButton = self.rightWidgetGroup.smallPlayModeButton
        self.moreActionsButton = self.rightWidgetGroup.moreActionsButton
        # 引用方法
        self.setCurrentTime = self.playProgressBar.setCurrentTime
        self.setTotalTime = self.playProgressBar.setTotalTime

    def updateSongInfoCard(self, songInfo: dict):
        """ 更新歌曲信息卡 """
        self.songInfoCard.updateSongInfoCard(songInfo)
        self.__adjustSongInfoCardWidth()

    def __adjustSongInfoCardWidth(self):
        """ 调整歌曲信息卡宽度 """
        if self.songInfoCard.width() + 20 >= self.playProgressBar.x():
            self.songInfoCard.setFixedWidth(self.playProgressBar.x() - 20)
            self.songInfoCard.scrollTextWindow.maxWidth = self.songInfoCard.width() - 155
            self.songInfoCard.scrollTextWindow.initFlagsWidth()
