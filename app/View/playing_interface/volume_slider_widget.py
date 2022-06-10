# coding:utf-8
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from components.buttons.circle_button import CircleButton
from components.widgets.slider import Slider
from PyQt5.QtCore import QEvent, QFile, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QWidget


class VolumeSliderWidget(QWidget):
    """ Volume slider widget """

    volumeLevelChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.volumeButton = VolumeButton(self)
        self.volumeSlider = Slider(Qt.Horizontal, self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedSize(345, 78)
        self.volumeButton.move(25, 15)
        self.volumeSlider.move(108, 25)
        self.volumeSlider.setSingleStep(1)
        self.volumeSlider.setRange(0, 100)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.volumeSlider.setObjectName('volumeSlider')
        setStyleSheet(self, 'volume_slider_widget')

        # connect signal to slot
        self.volumeButton.volumeLevelChanged.connect(self.volumeLevelChanged)
        self.volumeSlider.valueChanged.connect(
            self.volumeButton.setVolumeLevel)

    def paintEvent(self, e):
        """ paint widgets """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(QPen(QColor(190, 190, 190, 150)))
        painter.setBrush(QBrush(QColor(227, 227, 227)))
        painter.drawRoundedRect(self.rect(), 8, 8)

    def setVolume(self, volume: int):
        """ set volume """
        self.volumeSlider.setValue(volume)
        self.volumeButton.setVolumeLevel(volume)


class VolumeButton(CircleButton):
    """ Volume button """

    volumeLevelChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        self.__iconPaths = [
            ":/images/playing_interface/Volume0_black.png",
            ":/images/playing_interface/Volume1_black.png",
            ":/images/playing_interface/Volume2_black.png",
            ":/images/playing_interface/Volume3_black.png",
            ":/images/playing_interface/volume_black_level_mute_47_47.png",
        ]
        self.pixmap_list = [QPixmap(i) for i in self.__iconPaths]
        super().__init__(self.__iconPaths[0], parent)
        self.isMute = False
        self.__volumeLevel = 0

    def setVolumeLevel(self, volume):
        """ set volume level """
        if volume == 0:
            self.updateIcon(0)
        elif 0 < volume <= 32 and self.__volumeLevel != 1:
            self.updateIcon(1)
        elif 32 < volume <= 65 and self.__volumeLevel != 2:
            self.updateIcon(2)
        elif volume > 65 and self.__volumeLevel != 3:
            self.updateIcon(3)

    def updateIcon(self, iconIndex: int):
        """ update volume icon """
        self.__volumeLevel = iconIndex
        self.volumeLevelChanged.emit(iconIndex)

        if not self.isMute:
            self.iconPixmap = self.pixmap_list[iconIndex]
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
                    signalBus.muteStateChanged.emit(self.isMute)
                self.update()
        return False

    def setMute(self, isMute: bool):
        """ set whether to mute """
        if self.isMute == isMute:
            return
        self.isMute = isMute
        index = -1 if isMute else self.__volumeLevel
        self.iconPixmap = self.pixmap_list[index]
        self.update()
