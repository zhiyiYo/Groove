# coding:utf-8

from app.View.play_bar.more_actions_menu import MoreActionsMenu
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget

from .play_bar_buttons import (
    BasicCircleButton,
    FillScreenButton,
    LoopModeButton,
    PlayButton,
    PullUpArrow,
    RandomPlayButton,
    VolumeButton,
)
from .play_progress_bar import PlayProgressBar
from .volume_slider import VolumeSlider


class PlayBar(QWidget):
    """ 播放栏 """

    # 鼠标进入信号
    enterSignal = pyqtSignal()
    leaveSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建小部件
        self.__createWidget()
        # 初始化
        self.__initWidget()

    def __createWidget(self):
        """ 创建小部件 """
        self.moreActionsMenu = MoreActionsMenu(self, 0)
        self.playButton = PlayButton(self)
        self.volumeButton = VolumeButton(self)
        self.volumeSlider = VolumeSlider(self.window())
        self.fillScreenButton = FillScreenButton(self)
        self.playProgressBar = PlayProgressBar("3:10", parent=self)
        self.pullUpArrowButton = PullUpArrow(
            r"app\resource\images\playing_interface\上拉箭头_27_27.png", self
        )
        self.lastSongButton = BasicCircleButton(
            r"app\resource\images\playing_interface\lastSong_47_47.png", self
        )
        self.nextSongButton = BasicCircleButton(
            r"app\resource\images\playing_interface\nextSong_47_47.png", self
        )
        self.randomPlayButton = RandomPlayButton(
            [r"app\resource\images\playing_interface\randomPlay_47_47.png"], self
        )
        self.loopModeButton = LoopModeButton(
            [
                r"app\resource\images\playing_interface\列表循环_47_47.png",
                r"app\resource\images\playing_interface\单曲循环_47_47.png",
            ],
            self,
        )
        self.moreActionsButton = BasicCircleButton(
            r"app\resource\images\playing_interface\更多操作_47_47.png", self
        )
        self.showPlaylistButton = BasicCircleButton(
            r"app\resource\images\playing_interface\显示播放列表_47_47.png", self
        )
        self.smallPlayModeButton = BasicCircleButton(
            r"app\resource\images\playing_interface\最小模式播放_47_47.png", self
        )
        # 创建小部件列表
        self.__widget_list = [
            self.playButton,
            self.fillScreenButton,
            self.playProgressBar.progressSlider,
            self.pullUpArrowButton,
            self.lastSongButton,
            self.nextSongButton,
            self.randomPlayButton,
            self.loopModeButton,
            self.moreActionsButton,
            self.showPlaylistButton,
            self.smallPlayModeButton,
        ]

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(193)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.lastSongButton.move(17, 85)
        self.playButton.move(77, 85)
        self.nextSongButton.move(137, 85)
        self.randomPlayButton.move(197, 85)
        self.loopModeButton.move(257, 85)
        self.volumeButton.move(317, 85)
        self.moreActionsButton.move(387, 85)
        self.volumeSlider.hide()
        self.playProgressBar.move(0, 45)
        self.__moveButtons()
        # 信号连接到槽
        self.__connectSignalToSlot()
        # 引用小部件及其方法
        self.__referenceWidget()

    def __showVolumeSlider(self):
        """ 显示音量滑动条 """
        # 显示播放栏
        if not self.volumeSlider.isVisible():
            pos = self.mapToGlobal(self.volumeButton.pos())
            x = pos.x() + int(
                self.volumeButton.width() / 2 - self.volumeSlider.width() / 2
            )
            y = self.y() + 15
            self.volumeSlider.move(x, y)
            self.volumeSlider.show()
        else:
            # 隐藏音量条
            self.volumeSlider.hide()

    def __moveButtons(self):
        """ 移动按钮 """
        self.pullUpArrowButton.move(
            int(self.width() / 2 - self.pullUpArrowButton.width() / 2), 165
        )
        self.fillScreenButton.move(self.width() - 64, 85)
        self.smallPlayModeButton.move(self.width() - 124, 85)
        self.showPlaylistButton.move(self.width() - 184, 85)

    def resizeEvent(self, e):
        """ 改变尺寸时移动按钮 """
        super().resizeEvent(e)
        self.playProgressBar.resize(self.width(), 38)
        self.__moveButtons()

    def enterEvent(self, e):
        """ 鼠标进入时发出进入信号 """
        self.enterSignal.emit()

    def leaveEvent(self, e):
        """ 鼠标离开时发出离开信号 """
        self.leaveSignal.emit()

    def __referenceWidget(self):
        """ 引用小部件及其方法 """
        self.progressSlider = self.playProgressBar.progressSlider
        self.setCurrentTime = self.playProgressBar.setCurrentTime
        self.setTotalTime = self.playProgressBar.setTotalTime

    def __showMoreActionsMenu(self):
        """ 显示更多操作菜单 """
        globalPos = self.mapToGlobal(self.moreActionsButton.pos())
        x = globalPos.x() + self.moreActionsButton.width() + 10
        y = int(globalPos.y() + self.moreActionsButton.height() / 2 - 114 / 2)
        self.moreActionsMenu.exec(QPoint(x, y))

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.moreActionsButton.clicked.connect(self.__showMoreActionsMenu)
        self.volumeButton.clicked.connect(self.__showVolumeSlider)
        self.volumeSlider.muteStateChanged.connect(
            lambda muteState: self.volumeButton.setMute(muteState)
        )
        self.volumeSlider.volumeLevelChanged.connect(
            lambda volumeLevel: self.volumeButton.updateIcon(volumeLevel)
        )
        for widget in self.__widget_list:
            widget.clicked.connect(self.volumeSlider.hide)
