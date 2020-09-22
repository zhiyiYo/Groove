# coding:utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter,QIcon
from PyQt5.QtWidgets import QPushButton

from my_functions.perspective_transform_cv import PixmapPerspectiveTransform
from my_functions.get_pressed_pos import getPressedPos



class PerspectivePushButton(QPushButton):
    """ 可以进行透视变换的PushButton """

    def __init__(self, text:str='', parent=None, icon:QIcon=None):
        super().__init__(text, parent)
        self.__perspectiveTrans = PixmapPerspectiveTransform()
        self.__pressedPix = None
        self.__pressedPos = None
        if icon:
            self.setIcon(icon)
        
    def mousePressEvent(self, e):
        """ 鼠标点击窗口时进行透视变换 """
        super().mousePressEvent(e)
        self.grabMouse()
        # 截屏
        self.__perspectiveTrans.setPixmap(self.grab())
        # 获取鼠标点击位置
        self.__pressedPos = getPressedPos(self, e)
        # 根据鼠标点击位置的不同设置背景封面的透视变换
        if self.__pressedPos == 'left':
            self.__perspectiveTrans.setDstPoints(
                [3, 1], [self.__perspectiveTrans.width - 2, 1],
                [3, self.__perspectiveTrans.height - 2],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 1])
        elif self.__pressedPos == 'left-top':
            self.__perspectiveTrans.setDstPoints(
                [3, 2], [self.__perspectiveTrans.width - 1, 1],
                [1, self.__perspectiveTrans.height - 2],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 1])
        elif self.__pressedPos == 'left-bottom':
            self.__perspectiveTrans.setDstPoints(
                [3, 1], [self.__perspectiveTrans.width - 2, 1],
                [3, self.__perspectiveTrans.height - 3],
                [self.__perspectiveTrans.width - 1, self.__perspectiveTrans.height - 1])
        elif self.__pressedPos == 'top':
            self.__perspectiveTrans.setDstPoints(
                [2, 2], [self.__perspectiveTrans.width - 3, 2],
                [1, self.__perspectiveTrans.height - 2],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 2])
        elif self.__pressedPos == 'center':
            self.__perspectiveTrans.setDstPoints(
                [2, 2], [self.__perspectiveTrans.width - 3, 2],
                [2, self.__perspectiveTrans.height - 3],
                [self.__perspectiveTrans.width - 3, self.__perspectiveTrans.height - 3])
        elif self.__pressedPos == 'bottom':
            self.__perspectiveTrans.setDstPoints(
                [1, 1], [self.__perspectiveTrans.width - 2, 1],
                [3, self.__perspectiveTrans.height - 3],
                [self.__perspectiveTrans.width - 4, self.__perspectiveTrans.height - 3])
        elif self.__pressedPos == 'right-top':
            self.__perspectiveTrans.setDstPoints(
                [0, 0], [self.__perspectiveTrans.width - 4, 1],
                [1, self.__perspectiveTrans.height - 1],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 2])
        elif self.__pressedPos == 'right':
            self.__perspectiveTrans.setDstPoints(
                [1, 0], [self.__perspectiveTrans.width - 4, 1],
                [1, self.__perspectiveTrans.height - 1],
                [self.__perspectiveTrans.width - 4, self.__perspectiveTrans.height - 2])
        elif self.__pressedPos == 'right-bottom':
            self.__perspectiveTrans.setDstPoints(
                [1, 1], [self.__perspectiveTrans.width - 2, 1],
                [0, self.__perspectiveTrans.height - 1],
                [self.__perspectiveTrans.width - 4, self.__perspectiveTrans.height - 3])
        self.__pressedPix = self.__perspectiveTrans.getPerspectiveTransform(
            self.__perspectiveTrans.width, self.__perspectiveTrans.height).scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.update()

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时显示小部件 """
        self.releaseMouse()
        self.__pressedPos = None
        self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        """ 绘制背景 """
        if not self.__pressedPos:
            super().paintEvent(e)
            return
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        # 绘制背景图片
        painter.drawPixmap(self.rect(), self.__pressedPix)

    @property
    def pressedPos(self):
        """ 返回鼠标点击位置 """
        return self.__pressedPos
