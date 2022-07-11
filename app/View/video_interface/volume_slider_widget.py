# coding:utf-8
from common.style_sheet import setStyleSheet
from components.buttons.circle_button import CircleButton
from components.widgets.slider import Slider
from PyQt5.QtCore import QEvent, QFile, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel


class VolumeSliderWidget(QWidget):
    """ Volume slider widget """

    muteStateChanged = pyqtSignal(bool)
    volumeLevelChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.volumeButton = VolumeButton(self)
        self.volumeSlider = Slider(Qt.Horizontal, self)
        self.volumeLabel = QLabel('100', self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedSize(345, 78)
        self.volumeButton.move(25, 15)
        self.volumeSlider.move(90, 25)
        self.volumeSlider.setSingleStep(1)
        self.volumeSlider.setRange(0, 100)
        self.volumeLabel.move(300, 28)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.__setQss()
        self.__connectSignalToSlot()

    def __setQss(self):
        """ set style sheet """
        self.volumeSlider.setObjectName('volumeSlider')
        setStyleSheet(self, 'volume_slider_widget')

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(25, 25, 25)))
        painter.setBrush(QBrush(QColor(31, 31, 31)))
        painter.drawRoundedRect(self.rect(), 10, 10)

    def setVolume(self, volume: int):
        """ set volume """
        volume = min(100, max(volume, 0))
        self.volumeSlider.setValue(volume)
        self.__onVolumeChanged(volume)

    def __onVolumeChanged(self, volume: int):
        """ volume changed slot """
        self.volumeButton.setVolumeLevel(volume)
        self.volumeLabel.setText(str(volume))
        self.volumeLabel.adjustSize()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.volumeSlider.valueChanged.connect(self.__onVolumeChanged)
        self.volumeButton.muteStateChanged.connect(self.muteStateChanged)
        self.volumeButton.volumeLevelChanged.connect(self.volumeLevelChanged)


class VolumeButton(CircleButton):
    """ Volume button """

    muteStateChanged = pyqtSignal(bool)
    volumeLevelChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        self.__iconPaths = [
            ":/images/video_window/Volume0.png",
            ":/images/video_window/Volume1.png",
            ":/images/video_window/Volume2.png",
            ":/images/video_window/Volume3.png",
            ":/images/video_window/Volumex.png",
        ]
        self.pixmaps = [QPixmap(i) for i in self.__iconPaths]
        super().__init__(self.__iconPaths[0], parent)
        self.isMute = False
        self.__volumeLevel = 0

    def setVolumeLevel(self, volume: int):
        """ set volume level and update icon """
        if volume == 0:
            self.updateIcon(0)
        elif 0 < volume <= 32:
            self.updateIcon(1)
        elif 32 < volume <= 65:
            self.updateIcon(2)
        elif volume > 65:
            self.updateIcon(3)

    def updateIcon(self, iconIndex: int):
        """ update icon """
        if self.__volumeLevel == iconIndex:
            return

        self.__volumeLevel = iconIndex
        self.volumeLevelChanged.emit(iconIndex)
        if not self.isMute:
            self.iconPixmap = self.pixmaps[iconIndex]
            self.update()

    def eventFilter(self, obj, e):
        if obj == self:
            if e.type() in [QEvent.Enter, QEvent.Leave]:
                self.isEnter = not self.isEnter
                self.update()
            elif e.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonRelease]:
                self.isPressed = not self.isPressed
                if e.type() == QEvent.MouseButtonRelease:
                    self.setMute(not self.isMute)
                    self.muteStateChanged.emit(self.isMute)
                self.update()
        return False

    def setMute(self, isMute: bool):
        """ set mute """
        if self.isMute == isMute:
            return

        self.isMute = isMute
        index = -1 if isMute else self.__volumeLevel
        self.iconPixmap = self.pixmaps[index]
        self.update()
