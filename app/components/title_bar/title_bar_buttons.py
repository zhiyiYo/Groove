# coding:utf-8
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QToolButton


class BasicButton(QToolButton):
    """ 基本六态按钮 """

    def __init__(self, iconPaths: list, parent=None, iconSize: tuple = (57, 40)):
        super().__init__(parent=parent)
        self.iconPaths = iconPaths
        self.iconWidth, self.iconHeight = iconSize
        self.isWhiteIcon = False

        self.resize(self.iconWidth, self.iconHeight)
        self.setIconSize(QSize(self.width(), self.height()))
        self.setStyleSheet("border: none; margin: 0px")
        self.__updateIcon("normal")

    def enterEvent(self, e):
        self.__updateIcon("hover")

    def leaveEvent(self, e):
        self.__updateIcon("normal")

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            return
        self.__updateIcon("pressed")
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.RightButton:
            return
        self.__updateIcon("normal")
        super().mouseReleaseEvent(e)

    def setWhiteIcon(self, isWhite: bool):
        """ set icon color """
        self.isWhiteIcon = isWhite
        self.__updateIcon("normal")

    def __updateIcon(self, iconState: str):
        """ update icon """
        self.setIcon(
            QIcon(self.iconPaths[self.isWhiteIcon][iconState]))


class MaximizeButton(QPushButton):
    """ Maximize button """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.iconPaths = [
            [
                {
                    "normal": ":/images/title_bar/透明黑色最大化按钮_57_40.png",
                    "hover": ":/images/title_bar/绿色最大化按钮_hover_57_40.png",
                    "pressed": ":/images/title_bar/黑色最大化按钮_pressed_57_40.png",
                },
                {
                    "normal": ":/images/title_bar/白色最大化按钮_57_40.png",
                    "hover": ":/images/title_bar/绿色最大化按钮_hover_57_40.png",
                    "pressed": ":/images/title_bar/黑色最大化按钮_pressed_57_40.png",
                },
            ],
            [
                {
                    "normal": ":/images/title_bar/黑色向下还原按钮_57_40.png",
                    "hover": ":/images/title_bar/绿色向下还原按钮_hover_57_40.png",
                    "pressed": ":/images/title_bar/向下还原按钮_pressed_57_40.png",
                },
                {
                    "normal": ":/images/title_bar/白色向下还原按钮_57_40.png",
                    "hover": ":/images/title_bar/绿色向下还原按钮_hover_57_40.png",
                    "pressed": ":/images/title_bar/向下还原按钮_pressed_57_40.png",
                },
            ],
        ]
        self.resize(57, 40)
        self.isMax = False
        self.isWhiteIcon = False
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(
            QIcon(":/images/title_bar/透明黑色最大化按钮_57_40.png"))
        self.setIconSize(QSize(57, 40))

    def setWhiteIcon(self, isWhite: bool):
        """ set icon color """
        self.isWhiteIcon = isWhite
        self.__updateIcon("normal")

    def __updateIcon(self, iconState: str):
        """ update icon """
        self.setIcon(
            QIcon(self.iconPaths[self.isMax][self.isWhiteIcon][iconState]))

    def enterEvent(self, e):
        self.__updateIcon("hover")

    def leaveEvent(self, e):
        self.__updateIcon("normal")

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            return
        self.__updateIcon("pressed")
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.RightButton:
            return
        self.isMax = not self.isMax
        self.__updateIcon("normal")
        super().mouseReleaseEvent(e)

    def setMaxState(self, isMax: bool):
        """ set maximized state """
        if self.isMax == isMax:
            return
        self.isMax = isMax
        self.__updateIcon("normal")
