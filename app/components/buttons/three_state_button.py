# coding:utf-8
from common.icon import getIconColor
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

    def __init__(self, iconPaths: dict, parent=None, buttonSize=(40, 40), iconSize=None):
        """
        Parameters
        ----------
        iconPaths: dict
            con path dict, provide icons in `normal`, `hover` and `pressed` state

        parent:
            parent window

        button: tuple
            button size

        iconSize: tuple
            icon size
        """
        super().__init__(parent)
        self.iconPaths = iconPaths
        self.resize(*buttonSize)
        self.setIconSize(self.size() if not iconSize else QSize(*iconSize))
        self.setCursor(Qt.ArrowCursor)
        self.setStyleSheet('border: none; margin: 0px')
        self.setIcon(QIcon(iconPaths['normal']))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        if obj is self:
            if e.type() == QEvent.Enter:
                self.setIcon(QIcon(self.iconPaths['hover']))
            elif e.type() in [QEvent.Leave, QEvent.MouseButtonRelease]:
                self.setIcon(QIcon(self.iconPaths['normal']))
            elif e.type() == QEvent.MouseButtonPress:
                self.setIcon(QIcon(self.iconPaths['pressed']))

        return super().eventFilter(obj, e)



class RandomPlayAllButton(ThreeStatePushButton):
    """ Random play all button """

    def __init__(self, parent=None):
        color = getIconColor()
        iconPaths = {
            "normal": f":/images/random_play_all/Shuffle_{color}_normal.svg",
            "hover": f":/images/random_play_all/Shuffle_{color}_hover.svg",
            "pressed": f":/images/random_play_all/Shuffle_{color}_pressed.svg",
        }
        super().__init__(iconPaths, " Shuffle all (0)", (20, 20), parent)
        self.setText(" " + self.tr("Shuffle all") + ' (0)')
        self.setObjectName("randomPlayButton")

    def setNumber(self, number: int):
        """ set random played number """
        self.setText(" " + self.tr("Shuffle all") + f' ({number})')
        self.adjustSize()
