# coding:utf-8
from common.signal_bus import signalBus
from components.buttons.tooltip_button import TooltipButton
from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtMultimedia import QMediaPlaylist
from PyQt5.QtWidgets import QToolButton


class PlayButton(TooltipButton):
    """ Play button """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isPlaying = False
        self.isEnter = False
        self.isPressed = False
        self.iconPixmaps = [
            QPixmap(':/images/play_bar/Play.png'),
            QPixmap(':/images/play_bar/Pause.png')
        ]
        self.setToolTip(self.tr('Play'))
        self.setFixedSize(65, 65)
        self.setStyleSheet(
            "QToolButton{border:none;margin:0;background:transparent}")
        self.installEventFilter(self)

    def setPlay(self, play: bool = True):
        """ set play state """
        self.isPlaying = play
        self.setToolTip(self.tr('Pause') if play else self.tr('Play'))
        self.update()

    def eventFilter(self, obj, e):
        if obj == self and self.isEnabled():
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.isPlaying = not self.isPlaying
                self.isPressed = False
                self.update()
                return False
            if e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
                self.hideToolTip()
                self.isPressed = True
                self.update()
                return False

        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        super().enterEvent(e)
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.isEnter = False
        self.update()

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        if self.isPressed:
            painter.setPen(QPen(QColor(255, 255, 255, 120), 2))
            painter.drawEllipse(1, 1, 62, 62)
        elif self.isEnter:
            # paint a two color circle
            painter.setPen(QPen(QColor(255, 255, 255, 18)))
            painter.drawEllipse(1, 1, 62, 62)
            # paint background
            painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
            painter.drawEllipse(2, 2, 61, 61)
            painter.setPen(QPen(QColor(0, 0, 0, 39)))
            painter.drawEllipse(1, 1, 63, 63)
        else:
            painter.setPen(QPen(QColor(255, 255, 255, 50), 2))
            painter.drawEllipse(1, 1, 62, 62)

        # paint icon
        if not self.isPressed:
            iconPix = self.iconPixmaps[self.isPlaying]
            painter.drawPixmap(1, 1, 63, 63, iconPix)
        else:
            iconPix = self.iconPixmaps[self.isPlaying].scaled(
                58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(3, 3, 59, 59, iconPix)


class RandomPlayButton(TooltipButton):
    """ Random play button """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isSelected = False
        self.isPressed = False
        self.isEnter = False
        self.setFixedSize(47, 47)
        self.setStyleSheet(
            "QToolButton{border:none;margin:0;background:transparent}")
        self.setToolTip(self.tr('Random play: off'))
        self.installEventFilter(self)

    def setRandomPlay(self, isRandomPlay: bool):
        """ set whether to random play """
        if isRandomPlay == self.isSelected:
            return

        text = self.tr('Random play: on') if isRandomPlay else self.tr(
            'Random play: off')
        self.setToolTip(text)
        self.isSelected = isRandomPlay
        self.update()

    def eventFilter(self, obj, e):
        if obj == self:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.isSelected = not self.isSelected
                text = self.tr('Random play: on') if self.isSelected else self.tr(
                    'Random play: off')
                self.setToolTip(text)
                self.isPressed = False
                self.update()
                signalBus.randomPlayChanged.emit(self.isSelected)
                return False
            if e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
                self.hideToolTip()
                self.isPressed = True
                self.update()
                return False

        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        super().enterEvent(e)
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.isEnter = False
        self.update()

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        self.image = QPixmap(':/images/play_bar/Shuffle.png')

        if self.isSelected:
            bgBrush = QBrush(QColor(0, 0, 0, 106))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        if self.isPressed:
            painter.setPen(QPen(QColor(0, 0, 0, 45)))
            bgBrush = QBrush(QColor(0, 0, 0, 45))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
            self.image = self.image.scaled(
                44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(2, 2, 44, 44, self.image)
        elif self.isEnter:
            painter.setPen(QPen(QColor(0, 0, 0, 38)))
            bgBrush = QBrush(QColor(0, 0, 0, 26))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)

        # paint icon
        if not self.isPressed:
            painter.setPen(Qt.NoPen)
            painter.drawPixmap(1, 1, 45, 45, self.image)


class BasicButton(TooltipButton):
    """ Basic circle button """

    def __init__(self, iconPath: str, parent=None):
        super().__init__(parent)
        self.isEnter = False
        self.isPressed = False
        self.iconPixmap = QPixmap(iconPath)
        self.setFixedSize(47, 47)

    def enterEvent(self, e):
        super().enterEvent(e)
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.isEnter = False
        self.update()

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.hideToolTip()
        self.isPressed = True
        self.update()

    def mouseReleaseEvent(self, e):
        self.isPressed = False
        self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        """ paint button """
        image = self.iconPixmap
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        painter.setPen(Qt.NoPen)
        if self.isPressed:
            bgBrush = QBrush(QColor(0, 0, 0, 45))
            painter.setBrush(bgBrush)
            painter.drawEllipse(2, 2, 42, 42)
            image = self.iconPixmap.scaled(
                43, 43, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        elif self.isEnter:
            painter.setPen(QPen(QColor(0, 0, 0, 38)))
            bgBrush = QBrush(QColor(0, 0, 0, 26))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        painter.setPen(Qt.NoPen)

        # paint icon
        if not self.isPressed:
            painter.drawPixmap(1, 1, 45, 45, image)
        else:
            painter.drawPixmap(2, 2, 42, 42, image)


class LoopModeButton(TooltipButton):
    """ Loop mode button """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isEnter = False
        self.isPressed = False
        self.clickedTime = 0
        self.loopMode = QMediaPlaylist.Sequential
        self.__loopMode_list = [
            QMediaPlaylist.Sequential,
            QMediaPlaylist.Loop,
            QMediaPlaylist.CurrentItemInLoop
        ]
        self.iconPixmaps = [
            QPixmap(':/images/play_bar/RepeatAll.png'),
            QPixmap(':/images/play_bar/RepeatAll.png'),
            QPixmap(':/images/play_bar/RepeatOne.png')
        ]
        self.setFixedSize(47, 47)
        self.installEventFilter(self)
        self.__updateToolTip()

    def setLoopMode(self, loopMode: QMediaPlaylist.PlaybackMode):
        """ set loop mode """
        if self.loopMode == loopMode:
            return

        self.loopMode = loopMode
        self.clickedTime = self.__loopMode_list.index(loopMode)
        self.update()
        self.__updateToolTip()

    def eventFilter(self, obj, e):
        if obj == self:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clickedTime = (self.clickedTime + 1) % 3
                self.loopMode = self.__loopMode_list[self.clickedTime]
                self.__updateToolTip()
                self.update()
                signalBus.loopModeChanged.emit(self.loopMode)
                return False

        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        super().enterEvent(e)
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.isEnter = False
        self.update()

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.hideToolTip()
        self.isPressed = True
        self.update()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.isPressed = False
        self.update()

    def paintEvent(self, e):
        """ paint button """
        iconPixmap = self.iconPixmaps[self.clickedTime]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # paint background color
        if self.clickedTime != 0:
            brush = QBrush(QColor(0, 0, 0, 106))
            painter.setBrush(brush)
            painter.drawEllipse(1, 1, 44, 44)
        if self.isPressed:
            painter.setPen(QPen(QColor(0, 0, 0, 45)))
            bgBrush = QBrush(QColor(0, 0, 0, 45))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
            iconPixmap = iconPixmap.scaled(
                44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(2, 2, 44, 44, iconPixmap)
        elif self.isEnter and self.clickedTime == 0:
            painter.setPen(QPen(QColor(0, 0, 0, 38)))
            bgBrush = QBrush(QColor(0, 0, 0, 26))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)

        # paint icon
        painter.setPen(Qt.NoPen)
        if not self.isPressed:
            painter.setPen(Qt.NoPen)
            painter.drawPixmap(1, 1, 45, 45, iconPixmap)

    def __updateToolTip(self):
        """ update tooltip """
        if self.loopMode == QMediaPlaylist.Sequential:
            text = self.tr('Loop playback: off')
        elif self.loopMode == QMediaPlaylist.Loop:
            text = self.tr('Loop: list loop')
        else:
            text = self.tr('Loop: single loop')

        self.setToolTip(text)


class VolumeButton(TooltipButton):
    """ Volume button """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isEnter = False
        self.isPressed = False
        self.isMute = False
        self.currentVolumeLevel = 1
        self.iconPixmaps = [
            QPixmap(':/images/play_bar/Volume0.png'),
            QPixmap(':/images/play_bar/Volume1.png'),
            QPixmap(':/images/play_bar/Volume2.png'),
            QPixmap(':/images/play_bar/Volume3.png'),
            QPixmap(':/images/play_bar/Volumex.png')
        ]
        self.iconPixmap = self.iconPixmaps[1]
        self.setFixedSize(47, 47)
        self.setToolTip(self.tr('Mute: off'))

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.hideToolTip()
        self.isPressed = True
        self.update()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.isPressed = False
        self.setMute(not self.isMute)
        self.update()
        signalBus.muteStateChanged.emit(self.isMute)

    def enterEvent(self, e):
        super().enterEvent(e)
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.isEnter = False
        self.update()

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        painter.setPen(Qt.NoPen)
        if self.isPressed:
            bgBrush = QBrush(QColor(0, 0, 0, 45))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
            iconPixmap = self.iconPixmap.scaled(
                44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(1, 1, 44, 44, iconPixmap)
        elif self.isEnter:
            painter.setPen(QPen(QColor(0, 0, 0, 38)))
            bgBrush = QBrush(QColor(0, 0, 0, 26))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)

        # paint icon
        if not self.isPressed:
            painter.setPen(Qt.NoPen)
            brush = QBrush(self.iconPixmap)
            painter.setBrush(brush)
            painter.drawEllipse(1, 1, 45, 45)

    def setMute(self, isMute: bool):
        """ set whether to mute """
        if isMute == self.isMute:
            return

        text = self.tr('Mute: on') if isMute else self.tr('Mute: off')
        self.setToolTip(text)

        self.isMute = isMute
        index = -1 if isMute else self.currentVolumeLevel
        self.iconPixmap = self.iconPixmaps[index]
        self.update()

    def setVolumeLevel(self, volume):
        """ set volume level """
        if volume == 0:
            self.__updateIcon(0)
        elif volume <= 32 and self.currentVolumeLevel != 1:
            self.__updateIcon(1)
        elif 33 <= volume <= 65 and self.currentVolumeLevel != 2:
            self.__updateIcon(2)
        elif volume > 65 and self.currentVolumeLevel != 3:
            self.__updateIcon(3)

    def __updateIcon(self, iconIndex):
        """ update icon """
        self.currentVolumeLevel = iconIndex
        if not self.isMute:
            self.iconPixmap = self.iconPixmaps[iconIndex]
            self.update()
