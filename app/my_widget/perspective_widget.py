# coding:utf-8

from app.my_functions.get_pressed_pos import getPressedPos
from app.my_functions.perspective_transform_cv import \
    PixmapPerspectiveTransform
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPainter, QPixmap, QScreen
from PyQt5.QtWidgets import QApplication, QWidget


class PerspectiveWidget(QWidget):
    """ 可进行透视变换的窗口 """

    def __init__(self, parent=None, isTransScreenshot=False):
        super().__init__(parent)
        self.__visibleChildren = []
        self.__isTransScreenshot = isTransScreenshot
        self.__perspectiveTrans = PixmapPerspectiveTransform()
        self.__screenshotPix = None
        self.__pressedPix = None
        self.__pressedPos = None

    @property
    def pressedPos(self) -> str:
        """ 返回鼠标点击位置 """
        return self.__pressedPos

    def mousePressEvent(self, e):
        """ 鼠标点击窗口时进行透视变换 """
        super().mousePressEvent(e)
        # 多次点击时不响应，防止小部件的再次隐藏
        if self.__pressedPos:
            return
        self.grabMouse()
        pixmap = self.grab()
        self.__perspectiveTrans.setPixmap(pixmap)
        # 根据鼠标点击位置的不同设置背景封面的透视变换
        self.__setDstPointsByPressedPos(getPressedPos(self,e))
        # 获取透视变换后的QPixmap
        self.__pressedPix = self.__getTransformPixmap()
        # 对桌面上的窗口进行截图
        if self.__isTransScreenshot:
            self.__adjustTransformPix()
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

    def __setDstPointsByPressedPos(self,pressedPos:str):
        """ 通过鼠标点击位置设置透视变换的四个边角坐标 """
        self.__pressedPos = pressedPos
        if self.__pressedPos == 'left':
            self.__perspectiveTrans.setDstPoints(
                [5, 4], [self.__perspectiveTrans.width - 2, 1],
                [3, self.__perspectiveTrans.height - 3],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 1])
        elif self.__pressedPos == 'left-top':
            self.__perspectiveTrans.setDstPoints(
                [7, 6], [self.__perspectiveTrans.width - 1, 1],
                [1, self.__perspectiveTrans.height - 2],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 1])
        elif self.__pressedPos == 'left-bottom':
            self.__perspectiveTrans.setDstPoints(
                [0, 1], [self.__perspectiveTrans.width - 3, 0],
                [6, self.__perspectiveTrans.height - 5],
                [self.__perspectiveTrans.width - 2, self.__perspectiveTrans.height - 2])
        elif self.__pressedPos == 'top':
            self.__perspectiveTrans.setDstPoints(
                [4, 5], [self.__perspectiveTrans.width - 5, 5],
                [0, self.__perspectiveTrans.height - 1],
                [self.__perspectiveTrans.width - 1, self.__perspectiveTrans.height - 1])
        elif self.__pressedPos == 'center':
            self.__perspectiveTrans.setDstPoints(
                [3, 4], [self.__perspectiveTrans.width - 4, 4],
                [3, self.__perspectiveTrans.height - 3],
                [self.__perspectiveTrans.width - 4, self.__perspectiveTrans.height - 3])
        elif self.__pressedPos == 'bottom':
            self.__perspectiveTrans.setDstPoints(
                [0, 0], [self.__perspectiveTrans.width - 1, 0],
                [4, self.__perspectiveTrans.height - 4],
                [self.__perspectiveTrans.width - 5, self.__perspectiveTrans.height - 4])
        elif self.__pressedPos == 'right-bottom':
            self.__perspectiveTrans.setDstPoints(
                [1, 0], [self.__perspectiveTrans.width - 3, 2],
                [1, self.__perspectiveTrans.height - 2],
                [self.__perspectiveTrans.width - 6, self.__perspectiveTrans.height - 5])
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

    def __getTransformPixmap(self) -> QPixmap:
        """ 获取透视变换后的QPixmap """
        pix = self.__perspectiveTrans.getPerspectiveTransform(
            self.__perspectiveTrans.width, self.__perspectiveTrans.height).scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return pix

    def __getScreenShot(self) -> QPixmap:
        """ 对窗口口所在的桌面区域进行截图 """
        screen = QApplication.primaryScreen()  # type:QScreen
        pos = self.mapToGlobal(QPoint(0, 0))   # type:QPoint
        pix = screen.grabWindow(
            0, pos.x(), pos.y(), self.width(), self.height())
        return pix

    def __adjustTransformPix(self):
        """ 对窗口截图再次进行透视变换并将两张图融合，消除可能存在的黑边 """
        self.__screenshotPix = self.__getScreenShot()
        self.__perspectiveTrans.setPixmap(self.__screenshotPix)
        self.__screenshotPressedPix = self.__getTransformPixmap()
        # 融合两张透视图
        img_1 = self.__perspectiveTrans.transQPixmapToNdarray(self.__pressedPix)
        img_2 = self.__perspectiveTrans.transQPixmapToNdarray(self.__screenshotPressedPix)
        # 去除非透明背景部分
        mask = img_1[:, :, -1] == 0
        img_2[mask] = img_1[mask]
        self.__pressedPix = self.__perspectiveTrans.transNdarrayToQPixmap(img_2)
