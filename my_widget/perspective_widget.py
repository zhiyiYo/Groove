# coding:utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QWidget

from my_functions.perspective_transform_cv import PixmapPerspectiveTransForm
from my_functions.get_pressed_pos import getPressedPos


class PerspectiveWidget(QWidget):
    """ 可进行透视变换的窗口 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__visibleChildren = []
        self.__perspectiveTrans = PixmapPerspectiveTransForm()
        self.__fixedPixmap = None
        self.__pressedPix = None
        self.__pressedPos = None

    def setFixedPixmap(self, pixmap: QPixmap):
        """ 设置固定的pixmap用于透视变换 """
        self.__fixedPixmap = pixmap

    def mousePressEvent(self, e):
        """ 鼠标点击窗口时进行透视变换 """
        super().mousePressEvent(e)
        self.grabMouse()
        pixmap = self.grab() if not self.__fixedPixmap else self.__fixedPixmap
        self.__perspectiveTrans.setPixmap(pixmap)
        # 获取鼠标点击位置
        self.__pressedPos = getPressedPos(self, e)
        # 根据鼠标点击位置的不同设置背景封面的透视变换
        if self.__pressedPos == 'left':
            self.__perspectiveTrans.setDstPoints(
                [5, 4], [self.__perspectiveTrans.width - 2, 1],
                [3, self.__perspectiveTrans.height - 3],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 1])
        elif self.__pressedPos == 'left-top':
            self.__perspectiveTrans.setDstPoints(
                [6, 5], [self.__perspectiveTrans.width - 1, 1],
                [1, self.__perspectiveTrans.height - 2],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 1])
        elif self.__pressedPos == 'left-bottom':
            self.__perspectiveTrans.setDstPoints(
                [2, 3], [self.__perspectiveTrans.width - 3, 0],
                [4, self.__perspectiveTrans.height - 4],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 2])
        elif self.__pressedPos == 'top':
            self.__perspectiveTrans.setDstPoints(
                [3, 5], [self.__perspectiveTrans.width - 4, 5],
                [1, self.__perspectiveTrans.height - 2],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 2])
        elif self.__pressedPos == 'center':
            self.__perspectiveTrans.setDstPoints(
                [3, 4], [self.__perspectiveTrans.width - 4, 4],
                [3, self.__perspectiveTrans.height - 3],
                [self.__perspectiveTrans.width - 4, self.__perspectiveTrans.height - 3])
        elif self.__pressedPos == 'bottom':
            self.__perspectiveTrans.setDstPoints(
                [2, 2], [self.__perspectiveTrans.width - 3, 3],
                [3, self.__perspectiveTrans.height - 3],
                [self.__perspectiveTrans.width - 4, self.__perspectiveTrans.height - 3])
        elif self.__pressedPos == 'right-bottom':
            self.__perspectiveTrans.setDstPoints(
                [1, 0], [self.__perspectiveTrans.width - 3, 2],
                [1, self.__perspectiveTrans.height - 2],
                [self.__perspectiveTrans.width - 5, self.__perspectiveTrans.height - 4])
        elif self.__pressedPos == 'right-top':
            self.__perspectiveTrans.setDstPoints(
                [0, 1], [self.__perspectiveTrans.width - 7, 5],
                [2, self.__perspectiveTrans.height - 1],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 2])
        elif self.__pressedPos == 'right':
            self.__perspectiveTrans.setDstPoints(
                [1, 1], [self.__perspectiveTrans.width - 6, 4],
                [2, self.__perspectiveTrans.height - 1],
                [self.__perspectiveTrans.width - 4, self.__perspectiveTrans.height - 3])
        self.__pressedPix = self.__perspectiveTrans.getPerspectiveTransform(
            self.__perspectiveTrans.width, self.__perspectiveTrans.height, isGetQPixmap=True).scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # 隐藏本来看得见的小部件
        self.__visibleChildren = [
            child for child in self.children() if hasattr(child, 'isVisible') and child.isVisible()]
        for child in self.__visibleChildren:
            if hasattr(child, 'hide'):
                child.hide()
        self.update()

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时显示小部件 """
        super().mouseReleaseEvent(e)
        self.releaseMouse()
        self.__pressedPos = None
        self.update()
        # 显示小部件
        for child in self.__visibleChildren:
            if hasattr(child, 'show'):
                child.show()

    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        # 绘制背景图片
        if self.__pressedPos:
            painter.drawPixmap(self.rect(), self.__pressedPix)

    @property
    def pressedPos(self) -> str:
        """ 返回鼠标点击位置 """
        return self.__pressedPos
