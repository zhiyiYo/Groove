# coding:utf-8
from app.components.slider import Slider
from app.components.buttons.circle_button import CircleButton
from app.View.play_bar.more_actions_menu import MoreActionsMenu
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel

from .play_bar_buttons import (FullScreenButton, LoopModeButton, PlayButton,
                               PullUpArrow, RandomPlayButton, VolumeButton)
from .volume_slider_widget import VolumeSliderWidget


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
        self.volumeSliderWidget = VolumeSliderWidget(self.window())
        self.FullScreenButton = FullScreenButton(self)
        self.playProgressBar = PlayProgressBar("3:10", parent=self)
        self.pullUpArrowButton = PullUpArrow(
            r"app\resource\images\playing_interface\ChevronUp.png", self)
        self.lastSongButton = CircleButton(
            r"app\resource\images\playing_interface\Previous.png", self)
        self.nextSongButton = CircleButton(
            r"app\resource\images\playing_interface\Next.png", self)
        self.randomPlayButton = RandomPlayButton(
            [r"app\resource\images\playing_interface\randomPlay_47_47.png"], self)
        self.loopModeButton = LoopModeButton(
            [
                r"app\resource\images\playing_interface\RepeatAll.png",
                r"app\resource\images\playing_interface\RepeatOne.png",
            ],
            self,
        )
        self.moreActionsButton = CircleButton(
            r"app\resource\images\playing_interface\More.png", self)
        self.showPlaylistButton = CircleButton(
            r"app\resource\images\playing_interface\显示播放列表_47_47.png", self)
        self.smallPlayModeButton = CircleButton(
            r"app\resource\images\playing_interface\最小模式播放_47_47.png", self)
        # 创建小部件列表
        self.__widget_list = [
            self.playButton,
            self.FullScreenButton,
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
        self.volumeSliderWidget.hide()
        self.playProgressBar.move(0, 45)
        self.__moveButtons()
        # 信号连接到槽
        self.__connectSignalToSlot()
        # 引用小部件及其方法
        self.__referenceWidget()

    def __showVolumeSlider(self):
        """ 显示音量滑动条 """
        # 显示播放栏
        if not self.volumeSliderWidget.isVisible():
            pos = self.mapToGlobal(self.volumeButton.pos())
            x = pos.x() + int(
                self.volumeButton.width() / 2 - self.volumeSliderWidget.width() / 2
            )
            y = self.y() + 15
            self.volumeSliderWidget.move(x, y)
            self.volumeSliderWidget.show()
        else:
            # 隐藏音量条
            self.volumeSliderWidget.hide()

    def __moveButtons(self):
        """ 移动按钮 """
        self.pullUpArrowButton.move(
            self.width()//2 - self.pullUpArrowButton.width()//2, 165)
        self.FullScreenButton.move(self.width() - 64, 85)
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
        y = globalPos.y() + self.moreActionsButton.height()//2 - 114/2
        self.moreActionsMenu.exec(QPoint(x, y))

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.moreActionsButton.clicked.connect(self.__showMoreActionsMenu)
        self.volumeButton.clicked.connect(self.__showVolumeSlider)
        self.volumeSliderWidget.muteStateChanged.connect(self.volumeButton.setMute)
        self.volumeSliderWidget.volumeLevelChanged.connect(self.volumeButton.updateIcon)
        for widget in self.__widget_list:
            widget.clicked.connect(self.volumeSliderWidget.hide)


class PlayProgressBar(QWidget):
    """ 歌曲播放进度条 """

    def __init__(self, duration: str = "0:00", parent=None):
        super().__init__(parent)
        # 创建两个标签和一个进度条
        self.progressSlider = Slider(Qt.Horizontal, self)
        self.currentTimeLabel = QLabel("0:00", self)
        self.totalTimeLabel = QLabel(duration, self)
        # 初始化界面
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(38)
        self.progressSlider.move(73, 0)
        self.currentTimeLabel.move(33, 9)
        self.progressSlider.setObjectName("progressSlider")
        self.currentTimeLabel.setObjectName("timeLabel")
        self.totalTimeLabel.setObjectName("timeLabel")

    def setCurrentTime(self, currentTime: int):
        """ 更新当前时间标签

        Parameters
        ----------
        currentTime: int
            毫秒时间"""
        seconds, minutes = self.getSecondMinute(currentTime)
        self.currentTimeLabel.setText(f'{minutes}:{str(seconds).rjust(2,"0")}')
        self.currentTimeLabel.move(
            33 - 9 * (len(self.totalTimeLabel.text()) - 4), 9)

    def setTotalTime(self, totalTime):
        """ 更新总时长标签，totalTime的单位为ms """
        seconds, minutes = self.getSecondMinute(totalTime)
        self.totalTimeLabel.setText(f'{minutes}:{str(seconds).rjust(2,"0")}')

    def getSecondMinute(self, time):
        """ 将毫秒转换为分和秒 """
        seconds = int(time / 1000)
        minutes = seconds // 60
        seconds -= minutes * 60
        return seconds, minutes

    def resizeEvent(self, e):
        """ 改变尺寸时拉伸进度条 """
        self.progressSlider.resize(self.width() - 146, 38)
        self.totalTimeLabel.move(self.width() - 57, 10)
        super().resizeEvent(e)
