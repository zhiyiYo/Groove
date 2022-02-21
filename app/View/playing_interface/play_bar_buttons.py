# coding:utf-8
from common.signal_bus import signalBus
from components.buttons.circle_button import CircleButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtMultimedia import QMediaPlaylist


class SelectableButton(CircleButton):
    """ Selectable button """

    def __init__(self, iconPath_list: list, parent=None, iconSize=(47, 47), buttonSize=(47, 47)):
        super().__init__(iconPath_list[0], parent, iconSize, buttonSize)
        self.iconPath_list = iconPath_list
        self.isSelected = False
        self.selectableTime = len(self.iconPath_list)
        self.clickedTime = 0

    def mouseReleaseEvent(self, e):
        if not self.clickedTime:
            self.isSelected = True

        self.clickedTime += 1

        if self.clickedTime == self.selectableTime + 1:
            self.isSelected = False
            self.clickedTime = 0
            self.iconPixmap = QPixmap(self.iconPath_list[0])
        else:
            self.iconPixmap = QPixmap(self.iconPath_list[self.clickedTime - 1])

        self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        """ paint button """
        iconPixmap = self.iconPixmap
        px, py = self._pixPos_list[0]
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)

        if self.isPressed:
            if not self.isSelected:
                brush = QBrush(QColor(255, 255, 255, 70))
                pen = Qt.NoPen
            else:
                brush = QBrush(QColor(0, 0, 0, 83))
                pen = QPen(QColor(255, 255, 255, 160))
                pen.setWidthF(1.5)

            self.__drawCircle(painter, pen, brush)
            iconPixmap = self.iconPixmap.scaled(
                self.iconPixmap.width() - 4,
                self.iconPixmap.height() - 4,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            px, py = self._pixPos_list[1]
        else:
            if self.isSelected:
                pen = QPen(QColor(255, 255, 255, 100))
                pen.setWidthF(1.4)
                self.__drawCircle(painter, pen, QBrush(QColor(0, 0, 0, 60)))
            elif self.isEnter:
                painter.setOpacity(0.5)

        # paint icon
        painter.drawPixmap(px, py, iconPixmap.width(),
                           iconPixmap.height(), iconPixmap)

    def __drawCircle(self, painter, pen, brush):
        """ paint circle """
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.drawEllipse(1, 1, self.iconWidth - 2, self.iconHeight - 2)
        painter.setPen(pen)
        painter.drawEllipse(1, 1, self.iconWidth - 2, self.iconHeight - 2)


class RandomPlayButton(SelectableButton):
    """ Random play button """

    def __init__(self, iconPath_list: list, parent=None, iconSize=(47, 47), buttonSize=(47, 47)):
        super().__init__(iconPath_list, parent, iconSize, buttonSize)
        self.setToolTip(self.tr('Random play: off'))

    def setRandomPlay(self, isRandomPlay: bool):
        """ set whether to play randomly """
        if self.isSelected == isRandomPlay:
            return

        text = self.tr('Random play: on') if isRandomPlay else self.tr(
            'Random play: off')
        self.setToolTip(text)
        self.isSelected = isRandomPlay
        self.clickedTime = int(isRandomPlay)
        self.update()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        signalBus.randomPlayChanged.emit(self.isSelected)


class LoopModeButton(SelectableButton):
    """ Loop mode button """

    def __init__(self, iconPath_list: list, parent=None, iconSize=(47, 47), buttonSize=(47, 47)):
        super().__init__(iconPath_list, parent, iconSize, buttonSize)
        self.loopMode = QMediaPlaylist.Sequential
        self.__loopMode_list = [
            QMediaPlaylist.Sequential,
            QMediaPlaylist.Loop,
            QMediaPlaylist.CurrentItemInLoop,
        ]
        self.__updateToolTip()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.loopMode = self.__loopMode_list[self.clickedTime]
        signalBus.loopModeChanged.emit(self.loopMode)

    def setLoopMode(self, loopMode: QMediaPlaylist.PlaybackMode):
        """ set loop mode """
        if self.loopMode == loopMode:
            return

        self.loopMode = loopMode
        self.isSelected = self.loopMode in [
            QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop]
        self.clickedTime = self.__loopMode_list.index(loopMode)

        if self.clickedTime == 2:
            self.iconPixmap = QPixmap(self.iconPath_list[1])
        else:
            self.iconPixmap = QPixmap(self.iconPath_list[0])

        self.update()

    def update(self):
        super().update()
        self.__updateToolTip()

    def __updateToolTip(self):
        """ update tooltip """
        if self.loopMode == QMediaPlaylist.Sequential:
            text = self.tr('Loop playback: off')
        elif self.loopMode == QMediaPlaylist.Loop:
            text = self.tr('Loop: list loop')
        else:
            text = self.tr('Loop: single loop')

        self.setToolTip(text)


class PullUpArrow(CircleButton):
    """ Pull up arrow button """

    def __init__(self, iconPath, parent=None, iconSize=(27, 27), buttonSize=(27, 27)):
        super().__init__(iconPath, parent, iconSize, buttonSize)
        # the direction of rotation: 1 clockwise and -1 counterclockwise.
        self.rotateDirection = 1
        self.deltaAngleStep = 9
        self.totalRotateAngle = 0

        self.timer = QTimer(self)
        self.timer.setInterval(19)
        self.timer.timeout.connect(self.timerSlot)
        self.setToolTip(self.tr('Show playlist'))

    def setArrowDirection(self, direction: str = "up"):
        """ set the direction of arrow

        Parmeters
        ---------
        direction: str
            direction of arrow, including `up` and `down`
        """
        self.rotateDirection = 1 if direction.upper() == "UP" else -1
        self.totalRotateAngle = 0 if direction.upper() == "UP" else 180
        self.update()

    def timerSlot(self):
        """ timer time out slot """
        self.totalRotateAngle = (
            self.rotateDirection * self.deltaAngleStep + self.totalRotateAngle)
        self.update()
        if self.totalRotateAngle in [180, 0]:
            self.timer.stop()
            self.rotateDirection = -self.rotateDirection

    def mouseReleaseEvent(self, e):
        self.timer.start()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)

        if self.isPressed and self.rotateDirection == 1:
            brush = QBrush(QColor(0, 0, 0, 50))
            painter.setBrush(brush)
            painter.drawEllipse(0, 0, self.iconWidth, self.iconHeight)
        elif self.isEnter:
            painter.setOpacity(0.5)

        # paint icon
        painter.translate(13, 13)
        painter.rotate(self.totalRotateAngle)
        painter.drawPixmap(
            -int(self.iconWidth / 2), -
            int(self.iconHeight / 2), self.iconPixmap
        )


class TwoStateButton(CircleButton):
    """ Two state button """

    def __init__(self, iconPath_list, parent=None, isState_1=True):
        self.iconPath_list = iconPath_list
        super().__init__(self.iconPath_list[isState_1], parent)
        self._isState_1 = isState_1
        self.pixmap_list = [QPixmap(iconPath)
                            for iconPath in self.iconPath_list]
        self._pixPos_list = [(0, 0), (2, 2)]

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时更换图标 """
        self.setState(not self._isState_1)
        super().mouseReleaseEvent(e)

    def setState(self, isState_1: bool):
        """ set the state of button """
        if self._isState_1 == isState_1:
            return
        self._isState_1 = isState_1
        self.iconPixmap = self.pixmap_list[self._isState_1]
        self.update()


class PlayButton(TwoStateButton):
    """ Play button """

    def __init__(self, parent=None):
        self.iconPath_list = [
            ":/images/playing_interface/Pause_47_47.png",
            ":/images/playing_interface/Play_47_47.png",
        ]
        super().__init__(self.iconPath_list, parent)
        self.isPlay = False
        self.setToolTip(self.tr('Play'))

    def setPlay(self, isPlay: bool):
        """ set the play state """
        if self.isPlay == isPlay:
            return

        self.setToolTip(self.tr('Pause') if isPlay else self.tr('Play'))
        self.isPlay = isPlay
        self.setState(not isPlay)
        self.update()


class FullScreenButton(TwoStateButton):
    """ Full screen button """

    fullScreenChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        self.iconPath_list = [
            ":/images/playing_interface/FullScreen.png",
            ":/images/playing_interface/BackToWindow.png",
        ]
        super().__init__(self.iconPath_list, parent, False)
        self.__isFullScreen = False

    def setFullScreen(self, isFullScreen: bool):
        """ set full screen """
        if self.__isFullScreen == isFullScreen:
            return

        self.__isFullScreen = isFullScreen
        self.setState(self.__isFullScreen)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.__isFullScreen = not self.__isFullScreen
        self.fullScreenChanged.emit(self.__isFullScreen)

    def update(self):
        super().update()
        text = self.tr('Exit fullscreen') if self.__isFullScreen else self.tr(
            'Show fullscreen')
        self.setToolTip(text)


class VolumeButton(CircleButton):
    """ Volume button """

    def __init__(self, parent=None):
        self.__iconPaths = [
            ":/images/playing_interface/Volume0.png",
            ":/images/playing_interface/Volume1.png",
            ":/images/playing_interface/Volume2.png",
            ":/images/playing_interface/Volume3.png",
            ":/images/playing_interface/volume_white_level_mute_47_47.png",
        ]
        self.pixmap_list = [QPixmap(i) for i in self.__iconPaths]
        super().__init__(self.__iconPaths[0], parent)
        self.isMute = False
        self.__volumeLevel = 0
        self.setToolTip(self.tr('Volume'))

    def setMute(self, isMute: bool):
        """ set whether to mute """
        if self.isMute == isMute:
            return

        self.isMute = isMute
        index = -1 if isMute else self.__volumeLevel
        self.iconPixmap = self.pixmap_list[index]
        self.update()

    def setVolumeLevel(self, volume: int):
        """ set the volume level """
        if volume == 0:
            self.updateIcon(0)
        elif 0 < volume <= 32 and self.__volumeLevel != 1:
            self.updateIcon(1)
        elif 32 < volume <= 65 and self.__volumeLevel != 2:
            self.updateIcon(2)
        elif volume > 65 and self.__volumeLevel != 3:
            self.updateIcon(3)

    def updateIcon(self, iconIndex):
        """ update icon """
        self.__volumeLevel = iconIndex
        if not self.isMute:
            self.iconPixmap = self.pixmap_list[iconIndex]
            self.update()
