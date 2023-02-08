# coding:utf-8
from common.config import Theme, config
from common.audio_utils import getVolumeLevel
from common.style_sheet import setStyleSheet
from components.buttons.circle_button import CircleButton, CIF
from components.widgets.slider import Slider
from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel, QWidget


class VolumeWidget(QWidget):
    """ Volume widget """

    muteStateChanged = pyqtSignal(bool)
    volumeChanged = pyqtSignal(int)

    def __init__(self, parent=None, theme=Theme.AUTO):
        super().__init__(parent)
        self.theme = config.theme if theme == Theme.AUTO else theme
        self.volumeButton = VolumeButton(self, self.theme)
        self.volumeSlider = Slider(Qt.Horizontal, self)
        self.volumeLabel = QLabel('100', self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedSize(345, 78)
        self.volumeButton.move(25, 15)
        self.volumeSlider.move(90, 24)
        self.volumeSlider.setSingleStep(1)
        self.volumeSlider.setRange(0, 100)
        self.volumeLabel.move(300, 28)

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)

        setStyleSheet(self, 'volume_widget', self.theme)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.__connectSignalToSlot()

    def setVolume(self, volume: int):
        """ set volume """
        self.volumeSlider.setValue(volume)
        self.__onVolumeChanged(volume)

    def value(self):
        return self.volumeSlider.value()

    def __onVolumeChanged(self, volume: int):
        """ volume changed slot """
        self.volumeButton.setVolume(volume)
        self.volumeLabel.setText(str(volume))
        self.volumeLabel.adjustSize()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.volumeSlider.valueChanged.connect(self.__onVolumeChanged)
        self.volumeSlider.valueChanged.connect(self.volumeChanged)
        self.volumeButton.muteStateChanged.connect(self.muteStateChanged)

    def paintEvent(self, e):
        """ paint widgets """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        if self.theme == Theme.LIGHT:
            painter.setPen(QColor(190, 190, 190))
            painter.setBrush(QColor(235, 235, 235))
        else:
            painter.setPen(QColor(15, 15, 15))
            painter.setBrush(QColor(31, 31, 31))

        painter.drawRoundedRect(self.rect(), 10, 10)


class VolumeButton(CircleButton):
    """ Volume button """

    muteStateChanged = pyqtSignal(bool)

    def __init__(self, parent=None, theme=Theme.LIGHT):
        if theme == Theme.LIGHT:
            self.iconPaths = [
                CIF.path(CIF.VOLUME0_BLACK),
                CIF.path(CIF.VOLUME1_BLACK),
                CIF.path(CIF.VOLUME2_BLACK),
                CIF.path(CIF.VOLUME3_BLACK),
                CIF.path(CIF.VOLUMEX_BLACK),
            ]
        else:
            self.iconPaths = [
                CIF.path(CIF.VOLUME0_WHITE),
                CIF.path(CIF.VOLUME1_WHITE),
                CIF.path(CIF.VOLUME2_WHITE),
                CIF.path(CIF.VOLUME3_WHITE),
                CIF.path(CIF.VOLUMEX_WHITE),
            ]
        super().__init__(self.iconPaths[0], parent)
        self.isMute = False
        self.level = 0

    def setVolume(self, volume: int):
        """ set volume """
        level = getVolumeLevel(volume)
        if self.level == level:
            return

        self.level = level
        if not self.isMute:
            self.setIcon(self.iconPaths[level])

    def eventFilter(self, obj, e):
        if obj is self:
            if e.type() in [QEvent.Enter, QEvent.Leave]:
                self.isEnter = not self.isEnter
                self.update()
            elif e.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonRelease]:
                self.isPressed = not self.isPressed
                if e.type() == QEvent.MouseButtonRelease:
                    self.setMute(not self.isMute)
                    self.muteStateChanged.emit(self.isMute)
                self.update()

        return super().eventFilter(obj, e)

    def setMute(self, isMute: bool):
        """ set mute """
        if self.isMute == isMute:
            return

        self.isMute = isMute
        index = -1 if isMute else self.level
        self.setIcon(self.iconPaths[index])
