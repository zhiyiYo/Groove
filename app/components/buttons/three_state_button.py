# coding:utf-8
from common.icon import Icon
from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QPushButton, QToolButton


class ThreeStatePushButton(QPushButton):
    """ Three state push button class """

    def __init__(self, iconPaths: dict, text='', iconSize: tuple = (130, 17), parent=None):
        """
        Parameters
        ----------
        iconPaths: dict
            icon path dict, provide icons in `normal`, `hover` and `pressed` state

        parent:
            parent window

        iconSize: tuple
            icon size
        """
        super().__init__(text, parent)
        self.iconPaths = iconPaths
        self.setIcon(Icon(self.iconPaths['normal']))
        self.setIconSize(QSize(*iconSize))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        if obj is self:
            if e.type() in [QEvent.Enter, QEvent.HoverMove]:
                self.setIcon(Icon(self.iconPaths['hover']))
            elif e.type() in [QEvent.Leave, QEvent.MouseButtonRelease]:
                self.setIcon(Icon(self.iconPaths['normal']))
            elif e.type() == QEvent.MouseButtonPress:
                self.setIcon(Icon(self.iconPaths['pressed']))

        return False


class ThreeStateButton(QToolButton):
    """ Three state tool button class """

    def __init__(self, iconPaths: dict, parent=None, iconSize: tuple = (40, 40)):
        """
        Parameters
        ----------
        iconPaths: dict
            con path dict, provide icons in `normal`, `hover` and `pressed` state

        parent:
            parent window

        iconSize: tuple
            icon size
        """
        super().__init__(parent)
        self.__state = 'normal'
        self.iconPaths = iconPaths
        self.resize(*iconSize)
        self.setIconSize(self.size())
        self.setCursor(Qt.ArrowCursor)
        self.setStyleSheet('border: none; margin: 0px')

    def enterEvent(self, e):
        self.__updateIcon('hover')

    def leaveEvent(self, e):
        self.__updateIcon('normal')

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            return

        self.__updateIcon('pressed')
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.RightButton:
            return

        self.__updateIcon('normal')
        super().mouseReleaseEvent(e)

    def __updateIcon(self, state: str):
        if state == self.__state:
            return

        self.__state = state
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        painter.drawPixmap(self.rect(), QPixmap(self.iconPaths[self.__state]))
