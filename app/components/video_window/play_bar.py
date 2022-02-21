# coding:utf-8
from components.widgets.slider import HollowHandleStyle, Slider
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QLinearGradient, QPainter
from PyQt5.QtWidgets import QLabel, QWidget
from View.playing_interface.play_bar_buttons import (CircleButton,
                                                     FullScreenButton,
                                                     PlayButton, VolumeButton)

from .volume_slider_widget import VolumeSliderWidget


class PlayBar(QWidget):
    """ Play bar """

    progressSliderMoved = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.progressSlider = Slider(Qt.Horizontal, self)
        self.currentTimeLabel = QLabel('0:00', self)
        self.totalTimeLabel = QLabel('0:00', self)
        self.volumeButton = VolumeButton(self)
        self.playButton = PlayButton(self)
        self.fullScreenButton = FullScreenButton(self)
        self.skipBackButton = CircleButton(
            ":/images/video_window/SkipBack.png", self)
        self.skipForwardButton = CircleButton(
            ":/images/video_window/SkipForward.png", self)
        self.downloadButton = CircleButton(
            ":/images/video_window/Download.png", self)
        self.volumeSliderWidget = VolumeSliderWidget(self.window())

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.__setQss()
        self.resize(600, 250)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        # set the style of slider
        style = HollowHandleStyle({
            "groove.height": 4,
            "sub-page.color": QColor(72, 210, 242),
            "add-page.color": QColor(255, 255, 255, 50),
            "handle.color": QColor(72, 210, 242),
            "handle.ring-width": 2,
            "handle.hollow-radius": 10,
            "handle.margin": 0
        })
        self.progressSlider.setStyle(style)
        self.progressSlider.setFixedHeight(25)

        self.skipBackButton.setToolTip(self.tr('Rewind'))
        self.skipForwardButton.setToolTip(self.tr('Fast forward'))
        self.downloadButton.setToolTip(self.tr('Download'))
        self.fullScreenButton.setToolTip(self.tr('Show fullscreen'))
        for button in self.findChildren(CircleButton):
            button.setDarkToolTip(True)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ initialize layout """
        self.progressSlider.move(30, 100)
        self.currentTimeLabel.move(30, 130)
        self.volumeButton.move(30, 170)

    def __setQss(self):
        """ set style sheet """
        styleSheet = """
            QLabel {
                font: 14px 'Segoe UI', 'Microsoft YaHei';
                color: white;
            }

            PlayBar {
                background: transparent
            }
        """
        self.setStyleSheet(styleSheet)
        self.totalTimeLabel.adjustSize()

    def paintEvent(self, e):
        """ paint play bar """
        painter = QPainter(self)
        linear = QLinearGradient(0, 0, 0, self.height())
        linear.setColorAt(0, QColor(0, 0, 0, 0))
        linear.setColorAt(1, QColor(0, 0, 0, 204))
        painter.setPen(Qt.NoPen)
        painter.setBrush(linear)
        painter.drawRect(self.rect())

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.progressSlider.resize(
            self.width()-60, self.progressSlider.height())
        self.progressSlider.move(30, self.progressSlider.y())
        self.totalTimeLabel.move(
            self.width()-30-self.totalTimeLabel.width(), 124)
        self.playButton.move(self.width()//2-self.playButton.width()//2, 170)
        self.skipBackButton.move(
            self.playButton.x()-self.skipBackButton.width()-10, 170)
        self.skipForwardButton.move(
            self.playButton.x()+self.skipForwardButton.width()+10, 170)
        self.downloadButton.move(
            self.width()-self.downloadButton.width()-30, 170)
        self.fullScreenButton.move(
            self.downloadButton.x()-self.fullScreenButton.width()-10, 170)

    def setCurrentTime(self, currentTime: int):
        """ set current time

        Parameters
        ----------
        currentTime: int
            current time in milliseconds
        """
        self.currentTimeLabel.setText(self.__parseTime(currentTime))
        self.progressSlider.setValue(currentTime)
        self.currentTimeLabel.adjustSize()

    def setTotalTime(self, totalTime: int):
        """ set total time

        Parameters
        ----------
        totalTime:
            total time in milliseconds
        """
        self.progressSlider.setRange(0, totalTime)
        self.totalTimeLabel.setText(self.__parseTime(totalTime))
        self.totalTimeLabel.adjustSize()
        self.totalTimeLabel.move(
            self.width()-30-self.totalTimeLabel.width(), 124)

    @staticmethod
    def __parseTime(time: int) -> str:
        """ covert integer time to string """
        seconds = int(time / 1000)
        hours = seconds // 3600
        minutes = str(seconds // 60).rjust(2, "0")
        seconds = str(seconds % 60).rjust(2, "0")
        return f'{hours}:{minutes}:{seconds}'

    def __toggleVolumeWidget(self):
        """ toggle the visibility of volume widget """
        if not self.volumeSliderWidget.isVisible():
            pos = self.mapToGlobal(self.volumeButton.pos())
            self.volumeSliderWidget.move(self.window().x(), pos.y()-100)
            self.volumeSliderWidget.show()
        else:
            self.volumeSliderWidget.hide()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.progressSlider.clicked.connect(self.progressSliderMoved)
        self.progressSlider.sliderMoved.connect(self.progressSliderMoved)
        self.volumeButton.clicked.connect(self.__toggleVolumeWidget)
        self.volumeSliderWidget.volumeLevelChanged.connect(
            self.volumeButton.updateIcon)
        self.volumeSliderWidget.muteStateChanged.connect(
            self.volumeButton.setMute)
