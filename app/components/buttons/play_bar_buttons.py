# coding:utf-8
from common.icon import drawSvgIcon
from common.audio_utils import getVolumeLevel
from common.signal_bus import signalBus
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtMultimedia import QMediaPlaylist

from .circle_button import CircleButton, CircleButton, CIF


class SelectableButton(CircleButton):
    """ Selectable button """

    def __init__(self, iconPaths: list, parent=None, iconSize=(26, 26), buttonSize=(47, 47)):
        super().__init__(iconPaths[0], parent, iconSize, buttonSize)
        self.iconPaths = iconPaths
        self.isSelected = False
        self.selectableTime = len(self.iconPaths)
        self.clickedTime = 0

    def mouseReleaseEvent(self, e):
        if not self.clickedTime:
            self.isSelected = True

        self.clickedTime += 1

        if self.clickedTime == self.selectableTime + 1:
            self.isSelected = False
            self.clickedTime = 0
            self.setIcon(self.iconPaths[0])
        else:
            self.setIcon(self.iconPaths[self.clickedTime - 1])

        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)

        ds = 0
        if self.isPressed:
            ds = 3
            if not self.isSelected:
                brush = QBrush(QColor(255, 255, 255, 70))
                pen = Qt.NoPen
            else:
                brush = QBrush(QColor(0, 0, 0, 83))
                pen = QPen(QColor(255, 255, 255, 160), 1.5)

            self.__drawCircle(painter, pen, brush)
        else:
            if self.isSelected:
                pen = QPen(QColor(255, 255, 255, 100), 1.4)
                self.__drawCircle(painter, pen, QColor(0, 0, 0, 60))
            elif self.isEnter:
                painter.setOpacity(0.5)

        # draw icon
        self._drawIcon(painter, ds)

    def __drawCircle(self, painter, pen, brush):
        """ paint circle """
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)
        painter.setPen(pen)
        painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)


class RandomPlayButton(SelectableButton):
    """ Random play button """

    def __init__(self, parent=None):
        super().__init__([CIF.path(CIF.SHUFFLE)], parent)
        self.setToolTip(self.tr('Random play: off'))

    def setRandomPlay(self, isRandom: bool):
        """ set whether to play randomly """
        text = self.tr('Random play: on') if isRandom else self.tr(
            'Random play: off')
        self.setToolTip(text)
        self.isSelected = isRandom
        self.clickedTime = int(isRandom)
        self.update()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        signalBus.randomPlayChanged.emit(self.isSelected)


class DesktopLyricButton(SelectableButton):
    """ Desktop lyric button """

    lyricVisibleChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__([CIF.path(CIF.DESKTOP_LYRIC)], parent)
        self.setToolTip(self.tr('Desktop lyric: off'))

    def setLyricVisible(self, isVisible: bool):
        """ set the visibility of desktop lyric """
        text = self.tr('Desktop lyric: on') if isVisible else self.tr(
            'Desktop lyric: off')
        self.setToolTip(text)
        self.isSelected = isVisible
        self.clickedTime = int(isVisible)
        self.update()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.setLyricVisible(self.isSelected)
        self.lyricVisibleChanged.emit(self.isSelected)


class LoopModeButton(SelectableButton):
    """ Loop mode button """

    def __init__(self, parent=None):
        super().__init__([CIF.path(CIF.REPEAT_ALL),
                          CIF.path(CIF.REPEAT_ONE)], parent)
        self.loopMode = QMediaPlaylist.Sequential
        self.__loopModes = [
            QMediaPlaylist.Sequential,
            QMediaPlaylist.Loop,
            QMediaPlaylist.CurrentItemInLoop,
        ]
        self.__updateToolTip()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.loopMode = self.__loopModes[self.clickedTime]
        signalBus.loopModeChanged.emit(self.loopMode)

    def setLoopMode(self, mode: QMediaPlaylist.PlaybackMode):
        """ set loop mode """
        if self.loopMode == mode:
            return

        self.loopMode = mode
        self.isSelected = self.loopMode != QMediaPlaylist.Sequential
        self.clickedTime = self.__loopModes.index(mode)
        self.setIcon(self.iconPaths[int(self.clickedTime == 2)])

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

    def __init__(self, parent=None):
        super().__init__(CIF.path(CIF.CHEVRON_UP), parent, (16, 16), (27, 27))
        # the direction of rotation: 1 clockwise and -1 counterclockwise.
        self.angle = 0
        self.step = 9
        self.direction = 1

        self.timer = QTimer(self)
        self.timer.setInterval(19)
        self.timer.timeout.connect(self.__onTimeOut)
        self.setToolTip(self.tr('Show playlist'))

    def setArrowDirection(self, direction: str = "up"):
        """ set the direction of arrow

        Parmeters
        ---------
        direction: str
            direction of arrow, including `up` and `down`
        """
        self.direction = 1 if direction.lower() == "up" else -1
        self.angle = 0 if direction.lower() == "up" else 180
        self.update()

    def __onTimeOut(self):
        """ timer time out slot """
        self.angle = self.direction * self.step + self.angle
        self.update()
        if self.angle in [180, 0]:
            self.timer.stop()
            self.direction = -self.direction

    def mouseReleaseEvent(self, e):
        self.timer.start()
        super().mouseReleaseEvent(e)

    def rotate(self):
        self.timer.stop()
        self.timer.start()

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)

        if self.isPressed and self.direction == 1:
            painter.setBrush(QColor(0, 0, 0, 50))
            painter.drawEllipse(0, 0, self.width(), self.height())
        elif self.isEnter:
            painter.setOpacity(0.5)

        # draw icon
        painter.translate(13, 13)
        painter.rotate(self.angle)
        iw, ih = self.iconSize().width(), self.iconSize().height()
        drawSvgIcon(self.iconPath, painter, QRectF(-iw/2, -ih/2-1, iw, ih))


class TwoStateButton(CircleButton):
    """ Two state button """

    def __init__(self, iconPaths, parent=None, isState_1=True, iconSize=(26, 26), buttonSize=(47, 47)):
        super().__init__(iconPaths[isState_1], parent, iconSize, buttonSize)
        self.iconPaths = iconPaths
        self._isState_1 = isState_1

    def mouseReleaseEvent(self, e):
        self.setState(not self._isState_1)
        super().mouseReleaseEvent(e)

    def setState(self, isState_1: bool):
        """ set the state of button """
        if self._isState_1 == isState_1:
            return

        self._isState_1 = isState_1
        self.setIcon(self.iconPaths[self._isState_1])


class PlayButton(TwoStateButton):
    """ Play button """

    def __init__(self, parent=None):
        super().__init__([CIF.path(CIF.PAUSE), CIF.path(CIF.PLAY)], parent)
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
        super().__init__([CIF.path(CIF.FULL_SCREEN),
                          CIF.path(CIF.BACK_TO_WINDOW)], parent, False, (24, 24))
        self.__isFullScreen = False

    def setFullScreen(self, isFull: bool):
        """ set full screen """
        if self.__isFullScreen == isFull:
            return

        self.__isFullScreen = isFull
        self.setState(self.__isFullScreen)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.__isFullScreen = not self.__isFullScreen
        self.fullScreenChanged.emit(self.__isFullScreen)
        self.cancelHoverState()

    def update(self):
        super().update()
        text = self.tr('Exit fullscreen') if self.__isFullScreen else self.tr(
            'Show fullscreen')
        self.setToolTip(text)


class VolumeButton(CircleButton):
    """ Volume button """

    def __init__(self, parent=None):
        self.iconPaths = [
            CIF.path(CIF.VOLUME0_WHITE),
            CIF.path(CIF.VOLUME1_WHITE),
            CIF.path(CIF.VOLUME2_WHITE),
            CIF.path(CIF.VOLUME3_WHITE),
            CIF.path(CIF.VOLUMEX_WHITE),
        ]
        super().__init__(self.iconPaths[0], parent)
        self.level = 0
        self.isMute = False
        self.setToolTip(self.tr('Volume'))

    def setMute(self, isMute: bool):
        """ set whether to mute """
        if self.isMute == isMute:
            return

        self.isMute = isMute
        index = -1 if isMute else self.level
        self.setIcon(self.iconPaths[index])

    def setVolume(self, volume: int):
        """ set volume """
        level = getVolumeLevel(volume)
        if level == self.level:
            return

        self.level = level
        if not self.isMute:
            self.setIcon(self.iconPaths[level])


class ButtonFactory:
    """ Play bar button factory """

    PREVIOUS = 0
    PLAY = 1
    NEXT = 2
    RANDOM_PLAY = 3
    LOOP_MODE = 4
    VOLUME = 5
    MORE = 6
    PLAYLIST = 7
    SMALLEST_PLAY_MODE = 8
    FULL_SCREEN = 9
    PULL_UP_ARROW = 10
    SKIP_BACK = 11
    SKIP_FORWARD = 12
    DOWNLOAD = 13
    DESKTOP_LYRIC = 14

    @classmethod
    def create(cls, buttonType: int, parent=None):
        """ create button """
        if buttonType == cls.PLAY:
            return PlayButton(parent=parent)
        if buttonType == cls.RANDOM_PLAY:
            return RandomPlayButton(parent=parent)
        if buttonType == cls.LOOP_MODE:
            return LoopModeButton(parent=parent)
        if buttonType == cls.VOLUME:
            return VolumeButton(parent=parent)
        if buttonType == cls.FULL_SCREEN:
            return FullScreenButton(parent=parent)
        if buttonType == cls.PULL_UP_ARROW:
            return PullUpArrow(parent=parent)
        if buttonType == cls.DESKTOP_LYRIC:
            return DesktopLyricButton(parent=parent)
        if buttonType == cls.MORE:
            return CircleButton(CIF.path(CIF.MORE), parent)
        if buttonType == cls.DOWNLOAD:
            return CircleButton(CIF.path(CIF.DOWNLOAD), parent)
        if buttonType == cls.PLAYLIST:
            return CircleButton(CIF.path(CIF.PLAYLIST), parent)
        if buttonType == cls.SKIP_BACK:
            return CircleButton(CIF.path(CIF.SKIP_BACK), parent)
        if buttonType == cls.SKIP_FORWARD:
            return CircleButton(CIF.path(CIF.SKIP_FORWARD), parent)
        if buttonType == cls.SMALLEST_PLAY_MODE:
            return CircleButton(CIF.path(CIF.SMALLEST_PLAY_MODE), parent)
        if buttonType == cls.PREVIOUS:
            return CircleButton(CIF.path(CIF.PREVIOUS), parent, (23, 23))
        if buttonType == cls.NEXT:
            return CircleButton(CIF.path(CIF.NEXT), parent, (23, 23))
