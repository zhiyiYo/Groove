# coding:utf-8
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QApplication, QToolButton


class TitleBarButton(QToolButton):
    """ Title bar button """

    def __init__(self, size=(57, 40), parent=None):
        super().__init__(parent)
        self.resize(*size)
        self.__isWhiteIcon = False
        self.setProperty("isWhite", False)

    def setWhiteIcon(self, isWhite: bool):
        """ set icon color """
        if self.__isWhiteIcon == isWhite:
            return

        self.__isWhiteIcon = isWhite
        self.setProperty("isWhite", isWhite)
        self.setStyle(QApplication.style())


class MaximizeButton(TitleBarButton):
    """ Maximize button """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__isMax = False
        self.setProperty("isMax", False)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.__updateIcon(not self.__isMax)

        return super().mouseReleaseEvent(e)

    def setMaxState(self, isMax: bool):
        """ set maximized state """
        if self.__isMax == isMax:
            return

        self.__updateIcon(isMax)

    def __updateIcon(self, isMax):
        self.__isMax = isMax
        self.setProperty("isMax", isMax)
        self.setStyle(QApplication.style())
