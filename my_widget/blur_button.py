import sys

import numpy as np
from PIL import Image
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QBrush, QEnterEvent, QPainter, QPen, QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication,  QLabel, QToolButton, QWidget, QGraphicsOpacityEffect)
from scipy.ndimage.filters import gaussian_filter


class BlurButton(QToolButton):
    """ 歌手头像和专辑封面卡上的按钮 """

    def __init__(self, parent, buttonPos: tuple, iconPath, blurPicPath='', buttonSize: tuple = (70, 70), blurRadius=30):
        super().__init__(parent)
        # 动画效果
        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.showAni = QPropertyAnimation(self.opacityEffect, b'opacity')
        # 定时器
        # self.bigTimer = QTimer(self)
        # 保存属性
        self.blurPicPath = blurPicPath
        self.posX, self.posY = buttonPos
        self.buttonSize = buttonSize
        self.iconPath = iconPath
        self.blurRadius = blurRadius
        # 背景和磨砂特效
        self.blurPic = None
        # 设置鼠标进入标志位
        self.enter = False
        # 图标
        self.iconPic = QPixmap(self.iconPath).scaled(
            self.buttonSize[0], self.buttonSize[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # 初始化
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(self.buttonSize[0], self.buttonSize[1])
        self.move(self.posX, self.posY)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGraphicsEffect(self.opacityEffect)
        # 初始化动画
        self.showAni.setDuration(100)
        self.showAni.setStartValue(0)
        self.showAni.setEndValue(1)
        self.showAni.setEasingCurve(QEasingCurve.InQuad)
        self.__setBlurEffect()

    def __setBlurEffect(self):
        """ 设置磨砂效果 """
        if self.blurPicPath:
            # 裁剪下需要磨砂的部分
            image = np.array(Image.open(self.blurPicPath).resize((200, 200)).crop(
                (self.posX, self.posY, self.width()+self.posX, self.height()+self.posY)))
            blurImageArray = image
            # 对每一个颜色通道分别磨砂
            for i in range(3):
                blurImageArray[:, :, i] = gaussian_filter(
                    image[:, :, i], self.blurRadius)
            # 将narray转换为QImage
            height, width, bytesPerComponent = blurImageArray.shape
            bytesPerLine = 3 * width  # 每行的字节数
            self.blurPic = QPixmap.fromImage(
                QImage(blurImageArray.data, width, height, bytesPerLine, QImage.Format_RGB888))
            self.update()

    def setBlurPic(self, blurPicPath, blurRadius=35):
        """ 设置磨砂图片 """
        self.blurPicPath = blurPicPath
        self.blurRadius = blurRadius
        self.__setBlurEffect()

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        # 绘制磨砂背景和图标
        if not self.enter:
            if self.blurPic:
                self.__drawCirclePic(painter, 5, 5, self.width()-10,
                                     self.height() - 10, self.blurPic)
            self.__drawCirclePic(painter, 5, 5, self.width()-10,
                                 self.height() - 10, self.iconPic)
        else:
            if self.blurPic:
                self.__drawCirclePic(painter, 0, 0, self.width(
                ), self.height(), self.blurPic)
            self.__drawCirclePic(painter, 5, 5, self.width()-10,
                                 self.height() - 10, self.iconPic)

    def __drawCirclePic(self, painter, x, y, width, height, pixmap):
        """ 在指定区域画圆 """
        brush = QBrush(pixmap)
        painter.setBrush(brush)
        painter.drawEllipse(x, y, width, height)

    def enterEvent(self, e: QEnterEvent):
        """ 鼠标进入按钮时增大按钮并显示提示条 """
        self.enter = True
        self.update()

    def leaveEvent(self, e):
        """ 鼠标离开按钮时减小按钮并隐藏提示条 """
        self.enter = False
        self.update()

    def show(self):
        """ 淡入 """
        self.opacityEffect.setOpacity(0)
        super().show()
        self.showAni.start()


class Demo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(200, 200)
        self.picPath = 'resource\\Album Cover\\Attention\\Attention.jpg'
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap(self.picPath).scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.button = BlurButton(
            self, (35, 68), 'resource\\images\\添加到按钮_70_70.png', self.picPath, blurRadius=30)
        self.button.hide()

    def enterEvent(self, QEvent):
        self.button.show()

    def leaveEvent(self, QEvent):
        self.button.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
