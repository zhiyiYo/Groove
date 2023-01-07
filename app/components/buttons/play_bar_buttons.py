# coding:utf-8
from common.signal_bus import signalBus
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtMultimedia import QMediaPlaylist

from .circle_button import CircleButton


class SelectableButton(CircleButton):
    """ Selectable button """

    def __init__(self, iconPaths: list, parent=None, iconSize=(47, 47), buttonSize=(47, 47)):
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
            self.iconPixmap = QPixmap(self.iconPaths[0])
        else:
            self.iconPixmap = QPixmap(self.iconPaths[self.clickedTime - 1])

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

    def __init__(self, parent=None):
        iconPaths = [":/images/playing_interface/randomPlay_47_47.png"]
        super().__init__(iconPaths, parent, (47, 47), (47, 47))
        self.setToolTip(self.tr('Random play: off'))

    def setRandomPlay(self, isRandomPlay: bool):
        """ set whether to play randomly """
        text = self.tr('Random play: on') if isRandomPlay else self.tr(
            'Random play: off')
        self.setToolTip(text)
        self.isSelected = isRandomPlay
        self.clickedTime = int(isRandomPlay)
        self.update()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        signalBus.randomPlayChanged.emit(self.isSelected)


class DesktopLyricButton(SelectableButton):
    """ Desktop lyric button """

    lyricVisibleChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        iconPaths = [":/images/playing_interface/DesktopLyric.png"]
        super().__init__(iconPaths, parent, (47, 47), (47, 47))
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
        iconPaths = [
            ":/images/playing_interface/RepeatAll.png",
            ":/images/playing_interface/RepeatOne.png",
        ]
        super().__init__(iconPaths, parent, (47, 47), (47, 47))
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

    def setLoopMode(self, loopMode: QMediaPlaylist.PlaybackMode):
        """ set loop mode """
        if self.loopMode == loopMode:
            return

        self.loopMode = loopMode
        self.isSelected = self.loopMode in [
            QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop]
        self.clickedTime = self.__loopModes.index(loopMode)

        if self.clickedTime == 2:
            self.iconPixmap = QPixmap(self.iconPaths[1])
        else:
            self.iconPixmap = QPixmap(self.iconPaths[0])

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

    def __init__(self, parent=None):
        iconPath = ":/images/playing_interface/ChevronUp.png"
        super().__init__(iconPath, parent, (27, 27), (27, 27))
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

    def __init__(self, iconPaths, parent=None, isState_1=True):
        self.iconPaths = iconPaths
        super().__init__(self.iconPaths[isState_1], parent)
        self._isState_1 = isState_1
        self.pixmaps = [QPixmap(iconPath) for iconPath in self.iconPaths]
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
        self.iconPixmap = self.pixmaps[self._isState_1]
        self.update()


class PlayButton(TwoStateButton):
    """ Play button """

    def __init__(self, parent=None):
        self.iconPaths = [
            ":/images/playing_interface/Pause_47_47.png",
            ":/images/playing_interface/Play_47_47.png",
        ]
        super().__init__(self.iconPaths, parent)
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
        self.cancelHoverState()

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
        self.pixmaps = [QPixmap(i) for i in self.__iconPaths]
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
        self.iconPixmap = self.pixmaps[index]
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
            self.iconPixmap = self.pixmaps[iconIndex]
            self.update()


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
        buttonMap = {
            cls.PLAY: PlayButton,
            cls.RANDOM_PLAY: RandomPlayButton,
            cls.LOOP_MODE: LoopModeButton,
            cls.VOLUME: VolumeButton,
            cls.FULL_SCREEN: FullScreenButton,
            cls.PULL_UP_ARROW: PullUpArrow,
            cls.DESKTOP_LYRIC: DesktopLyricButton
        }
        if buttonType in buttonMap:
            return buttonMap[buttonType](parent)

        iconMap = {
            cls.PREVIOUS: ":/images/playing_interface/Previous.png",
            cls.NEXT: ":/images/playing_interface/Next.png",
            cls.MORE: ":/images/playing_interface/More.png",
            cls.PLAYLIST: ":/images/playing_interface/Playlist_47_47.png",
            cls.SMALLEST_PLAY_MODE: ":/images/playing_interface/SmallestPlayMode.png",
            cls.SKIP_BACK: ":/images/video_window/SkipBack.png",
            cls.SKIP_FORWARD: ":/images/video_window/SkipForward.png",
            cls.DOWNLOAD: ":/images/video_window/Download.png",
        }
        return CircleButton(iconMap[buttonType], parent)
