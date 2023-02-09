# coding:utf-8
from common.icon import drawSvgIcon
from components.buttons.circle_button import CIF
from PyQt5.QtCore import Qt, QEvent, QSize, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QToolButton


class SmallestPlayModeButton(QToolButton):
    """ Smallest interface button """

    def __init__(self, iconPath, parent=None, iconSize=(24, 24), buttonSize=(45, 45)):
        super().__init__(parent)
        self.isEnter = False
        self.isPressed = False

        self.iconPath = iconPath
        self.setIconSize(QSize(*iconSize))
        self.resize(*buttonSize)
        self.installEventFilter(self)

    def eventFilter(self, obj, e: QEvent):
        if obj is self:
            if e.type() == QEvent.Enter:
                self.isEnter = True
                self.update()
            elif e.type() == QEvent.Leave:
                self.isEnter = False
                self.update()
            elif e.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonDblClick, QEvent.MouseButtonRelease]:
                self.isPressed = not self.isPressed
                self.update()

        return super().eventFilter(obj, e)

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        ds = 0
        if self.isPressed:
            ds = 4
            pen = QPen(QColor(255, 255, 255, 30), 2)
        elif self.isEnter:
            pen = QPen(QColor(255, 255, 255, 96), 2)
        else:
            pen = Qt.NoPen

        # draw circle
        painter.setPen(pen)
        painter.drawEllipse(1, 1, self.width()-2, self.height()-2)

        # draw icon
        iw, ih = self.iconSize().width()-ds, self.iconSize().height()-ds
        rect = QRectF((self.width()-iw)/2, (self.height()-ih)/2, iw, ih)
        drawSvgIcon(self.iconPath, painter, rect)


class PlayButton(SmallestPlayModeButton):
    """ Play button """

    def __init__(self, parent=None, isPause=True):
        self.__isPause = isPause
        self.iconPaths = [
            ":/images/smallest_play_interface/Pause.svg",
            ":/images/smallest_play_interface/Play.svg",
        ]
        super().__init__(self.iconPaths[isPause], parent, (34, 34), (45, 45))

    def mouseReleaseEvent(self, e):
        self.setPlay(self.__isPause)
        super().mouseReleaseEvent(e)

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.__isPause = not isPlay
        self.iconPath = self.iconPaths[self.__isPause]
        self.update()