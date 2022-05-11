# coding:utf-8
from components.buttons.circle_button import CircleButton
from components.buttons.play_bar_buttons import (FullScreenButton,
                                                 LoopModeButton, PlayButton,
                                                 PullUpArrow, RandomPlayButton,
                                                 VolumeButton)
from components.widgets.label import TimeLabel
from components.widgets.menu import PlayingInterfaceMoreActionsMenu
from components.widgets.slider import HollowHandleStyle, Slider
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget

from .volume_slider_widget import VolumeSliderWidget


class PlayBar(QWidget):
    """ Play bar """

    enterSignal = pyqtSignal()
    leaveSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__createWidget()
        self.__initWidget()

    def __createWidget(self):
        """ create widgets """
        self.moreActionsMenu = PlayingInterfaceMoreActionsMenu(self)
        self.playButton = PlayButton(self)
        self.volumeButton = VolumeButton(self)
        self.volumeSliderWidget = VolumeSliderWidget(self.window())
        self.fullScreenButton = FullScreenButton(self)
        self.playProgressBar = PlayProgressBar(parent=self)
        self.pullUpArrowButton = PullUpArrow(self)
        self.lastSongButton = CircleButton(
            ":/images/playing_interface/Previous.png", self)
        self.nextSongButton = CircleButton(
            ":/images/playing_interface/Next.png", self)
        self.randomPlayButton = RandomPlayButton(self)
        self.loopModeButton = LoopModeButton(self)
        self.moreActionsButton = CircleButton(
            ":/images/playing_interface/More.png", self)
        self.showPlaylistButton = CircleButton(
            ":/images/playing_interface/Playlist_47_47.png", self)
        self.smallPlayModeButton = CircleButton(
            ":/images/playing_interface/SmallestPlayMode.png", self)

        self.__widget_list = [
            self.playButton,
            self.fullScreenButton,
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
        """ initialize widgets """
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
        self.lastSongButton.setToolTip(self.tr('Previous'))
        self.nextSongButton.setToolTip(self.tr('Next'))
        self.moreActionsButton.setToolTip(self.tr('More actions'))
        self.showPlaylistButton.setToolTip(self.tr('Show playlist'))
        self.smallPlayModeButton.setToolTip(self.tr('Smallest play mode'))
        self.__moveButtons()
        self.__connectSignalToSlot()
        self.__referenceWidget()

    def __showVolumeSlider(self):
        """ show volume slider """
        if not self.volumeSliderWidget.isVisible():
            pos = self.mapToGlobal(self.volumeButton.pos())
            x = pos.x() + int(
                self.volumeButton.width() / 2 - self.volumeSliderWidget.width() / 2)
            y = self.y() + 15
            self.volumeSliderWidget.move(x, y)
            self.volumeSliderWidget.show()
        else:
            self.volumeSliderWidget.hide()

    def __moveButtons(self):
        """ move buttons """
        self.pullUpArrowButton.move(
            self.width()//2 - self.pullUpArrowButton.width()//2, 165)
        self.fullScreenButton.move(self.width() - 64, 85)
        self.smallPlayModeButton.move(self.width() - 124, 85)
        self.showPlaylistButton.move(self.width() - 184, 85)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.playProgressBar.resize(self.width(), 38)
        self.__moveButtons()

    def enterEvent(self, e):
        self.enterSignal.emit()

    def leaveEvent(self, e):
        self.leaveSignal.emit()

    def __referenceWidget(self):
        self.progressSlider = self.playProgressBar.progressSlider
        self.setCurrentTime = self.playProgressBar.setCurrentTime
        self.setTotalTime = self.playProgressBar.setTotalTime

    def __showMoreActionsMenu(self):
        """ show more actions menu """
        pos = self.mapToGlobal(self.moreActionsButton.pos())
        x = pos.x() + self.moreActionsButton.width() + 10
        y = pos.y() + self.moreActionsButton.height()//2 - self.moreActionsMenu.height()/2
        self.moreActionsMenu.exec(QPoint(x, y))

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.moreActionsButton.clicked.connect(self.__showMoreActionsMenu)
        self.volumeButton.clicked.connect(self.__showVolumeSlider)
        self.volumeSliderWidget.volumeLevelChanged.connect(
            self.volumeButton.updateIcon)
        for widget in self.__widget_list:
            widget.clicked.connect(self.volumeSliderWidget.hide)


class PlayProgressBar(QWidget):
    """ Play progress bar """

    def __init__(self, duration: int = 0, parent=None):
        """
        Parameters
        ----------
        duration: int
            duration on seconds

        parent:
            parent window
        """
        super().__init__(parent)
        self.progressSlider = Slider(Qt.Horizontal, self)
        self.currentTimeLabel = TimeLabel(0, self)
        self.totalTimeLabel = TimeLabel(duration, self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedHeight(24)
        self.progressSlider.move(73, 0)

        # set the style of slider
        style = HollowHandleStyle({
            "handle.ring-width": 3,
            "handle.hollow-radius": 9,
            "handle.margin": 0
        })
        self.progressSlider.setStyle(style)
        self.progressSlider.setFixedHeight(24)
        self.currentTimeLabel.setObjectName("timeLabel")
        self.totalTimeLabel.setObjectName("timeLabel")

    def setCurrentTime(self, currentTime: int):
        """ set current time in milliseconds """
        self.currentTimeLabel.setTime(int(currentTime/1000))
        self.currentTimeLabel.move(
            33 - 9 * (len(self.totalTimeLabel.text()) - 4), 1)

    def setTotalTime(self, totalTime):
        """ set total time in milliseconds """
        self.totalTimeLabel.setTime(int(totalTime/1000))

    def resizeEvent(self, e):
        self.progressSlider.resize(self.width() - 146, 24)
        self.totalTimeLabel.move(self.width() - 57, 1)
        self.currentTimeLabel.move(33, 1)
        super().resizeEvent(e)
