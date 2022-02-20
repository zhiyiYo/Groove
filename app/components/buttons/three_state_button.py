# coding:utf-8
from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QIcon
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
        self.setIcon(QIcon(self.iconPaths['normal']))
        self.setIconSize(QSize(*iconSize))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        if obj is self:
            if e.type() in [QEvent.Enter, QEvent.HoverMove]:
                self.setIcon(QIcon(self.iconPaths['hover']))
            elif e.type() in [QEvent.Leave, QEvent.MouseButtonRelease]:
                self.setIcon(QIcon(self.iconPaths['normal']))
            elif e.type() == QEvent.MouseButtonPress:
                self.setIcon(QIcon(self.iconPaths['pressed']))

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
        self.iconPaths = iconPaths
        self.resize(*iconSize)
        self.initWidget()

    def initWidget(self):
        self.setCursor(Qt.ArrowCursor)
        self.setIcon(QIcon(self.iconPaths['normal']))
        self.setIconSize(QSize(self.width(), self.height()))
        self.setStyleSheet('border: none; margin: 0px')

    def enterEvent(self, e):
        self.setIcon(QIcon(self.iconPaths['hover']))

    def leaveEvent(self, e):
        self.setIcon(QIcon(self.iconPaths['normal']))

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            return

        self.setIcon(QIcon(self.iconPaths['pressed']))
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.RightButton:
            return

        self.setIcon(QIcon(self.iconPaths['normal']))
        super().mouseReleaseEvent(e)
