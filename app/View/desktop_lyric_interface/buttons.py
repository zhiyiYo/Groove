# coding:utf-8
from common.icon import drawSvgIcon
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPixmap, QColor
from PyQt5.QtWidgets import QToolButton


class Button(QToolButton):

    def __init__(self, iconPath: str, parent=None):
        super().__init__(parent=parent)
        self.__isEnter = False
        self.__isPressed = False
        self.iconPath = iconPath
        self.setFixedSize(30, 30)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, e):
        self.__isEnter = True
        self.update()

    def leaveEvent(self, e):
        self.__isEnter = False
        self.update()

    def mousePressEvent(self, e):
        self.__isPressed = True
        self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.__isPressed = False
        self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)

        # draw background
        if self.__isPressed:
            painter.setBrush(QColor(255, 255, 255, 67))
            painter.drawRoundedRect(self.rect(), 4, 4)
        elif self.__isEnter:
            painter.setBrush(QColor(255, 255, 255, 51))
            painter.drawRoundedRect(self.rect(), 4, 4)

        # draw icon
        if self.iconPath.endswith('svg'):
            drawSvgIcon(self.iconPath, painter, QRectF(
                (self.width()-16)/2, (self.height()-16)/2, 16, 16))
        else:
            painter.drawPixmap(self.rect(), QPixmap(self.iconPath))


class PlayButton(Button):
    """ Play/Pause button """

    def __init__(self, parent=None):
        self.isPlaying = False
        self.iconPaths = [
            ":/images/desktop_lyric_interface/Play.svg",
            ":/images/desktop_lyric_interface/Pause.svg"
        ]
        super().__init__(self.iconPaths[0], parent)

    def setPlay(self, play: bool):
        """ set play state """
        self.isPlaying = play
        self.iconPath = self.iconPaths[self.isPlaying]
        self.update()


class ButtonFactory:
    """ Button factory """

    ICON = 0
    PREVIOUS = 1
    PLAY = 2
    NEXT = 3
    LOCK = 4
    SETTING = 5
    CLOSE = 6
    FONT_INCREASE = 7
    FONT_DECREASE = 8

    @classmethod
    def create(cls, buttonType: int, parent=None):
        if buttonType == cls.PLAY:
            return PlayButton(parent)

        iconPaths = [
            ":/images/logo/logo_30_30.png",
            ":/images/desktop_lyric_interface/Previous.svg",
            ":/images/desktop_lyric_interface/Pause.svg",
            ":/images/desktop_lyric_interface/Next.svg",
            ":/images/desktop_lyric_interface/Lock.svg",
            ":/images/desktop_lyric_interface/Setting.svg",
            ":/images/desktop_lyric_interface/Close.svg",
            ":/images/desktop_lyric_interface/FontIncrease.svg",
            ":/images/desktop_lyric_interface/FontDecrease.svg",
        ]
        if not 0 <= buttonType <= len(iconPaths)-1:
            raise ValueError("The buttonType is illegal")

        return Button(iconPaths[buttonType], parent=parent)
