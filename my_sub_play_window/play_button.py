# coding:utf-8

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QToolButton


class PlayButton(QToolButton):
    """ 播放按钮 """

    def __init__(self, parent=None, isPaused=True):
        super().__init__(parent)
        # 图标地址列表
        self.__iconPath_dict = [
            {'normal': r'resource\images\sub_play_window\play_50_50_normal.png',
             'hover': r'resource\images\sub_play_window\play_50_50_hover.png',
             'pressed': r'resource\images\sub_play_window\play_50_50_pressed.png'},
            {'normal': r'resource\images\sub_play_window\pause_50_50_normal.png',
             'hover': r'resource\images\sub_play_window\pause_50_50_hover.png',
             'pressed': r'resource\images\sub_play_window\pause_50_50_pressed.png'}]
        # 暂停标志位
        self.isPaused = isPaused
        # 初始化小部件
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(50, 50)
        self.setCursor(Qt.ArrowCursor)
        self.setIcon(QIcon(self.__iconPath_dict[self.isPaused]['normal']))
        self.setIconSize(QSize(self.width(), self.height()))
        self.setStyleSheet('border: none; margin: 0px')

    def enterEvent(self, e):
        """ hover时更换图标 """
        self.setIcon(QIcon(self.__iconPath_dict[self.isPaused]['hover']))

    def leaveEvent(self, e):
        """ leave时更换图标 """
        self.setIcon(QIcon(self.__iconPath_dict[self.isPaused]['normal']))

    def mousePressEvent(self, e):
        """ 鼠标左键按下时更换图标 """
        if e.button() == Qt.RightButton:
            return
        self.setIcon(QIcon(self.__iconPath_dict[self.isPaused]['pressed']))
        self.isPaused = not self.isPaused
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时更换按钮图标 """
        if e.button() == Qt.RightButton:
            return
        self.setIcon(QIcon(self.__iconPath_dict[self.isPaused]['normal']))
        super().mouseReleaseEvent(e)

    def setPlay(self, isPlay: bool):
        """ 设置播放状态 """
        self.isPaused = not isPlay
        self.setIcon(QIcon(self.__iconPath_dict[self.isPaused]['normal']))
