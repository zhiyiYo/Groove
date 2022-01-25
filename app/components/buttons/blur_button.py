# coding:utf-8
from .tooltip_button import TooltipButton
from PIL import Image
from PIL.ImageFilter import GaussianBlur
from PyQt5.QtCore import QPoint, QPropertyAnimation, Qt, pyqtProperty
from PyQt5.QtGui import QBrush, QEnterEvent, QPainter, QPixmap
from PyQt5.QtWidgets import QToolButton


class BlurButton(TooltipButton):
    """ 磨砂按钮 """

    def __init__(self, parent, cropPos: tuple, iconPath: str, blurPicPath: str,
                 text: str, radius=35, blurRadius=40):
        """ 实例化磨砂按钮

        Parameters
        ----------
        parent:
            父级

        cropPos: tuple
            图像裁剪位置坐标

        iconPath: str
            按钮图标路径

        blurPicPath: str
            磨砂图片路径

        text: str
            按钮工具提示的文本

        radius: int
            按钮半径

        blurRadius: int
            磨砂半径
        """
        super().__init__(parent=parent)
        self.__paintRadius = radius-5
        self.radius = radius
        self.resize(radius*2, radius*2)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.blurPix = None
        self.blurPicPath = blurPicPath
        self.blurRadius = blurRadius
        self.cropX, self.cropY = cropPos
        self.iconPix = QPixmap(iconPath).scaled(
            radius*2, radius*2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.radiusAni = QPropertyAnimation(self, b'paintRadius', self)
        self.setToolTip(text)

    def showEvent(self, e):
        if not self.blurPix:
            self.__blur()

        self.__paintRadius=self.radius-5
        super().showEvent(e)

    def setBlurPic(self, blurPicPath, blurRadius=35):
        """ 设置磨砂图片 """
        if self.blurPicPath == blurPicPath:
            return
        self.blurPicPath = blurPicPath
        self.blurRadius = blurRadius
        self.blurPix = None

    def __blur(self):
        """ 真正进行磨砂操作 """
        if not self.blurPicPath.startswith(':'):
            img = Image.open(self.blurPicPath)
        else:
            img = Image.fromqpixmap(QPixmap(self.blurPicPath))

        img = img.convert('RGB').resize((200, 200))
        img = img.crop((self.cropX, self.cropY,
                        self.width() + self.cropX, self.height() + self.cropY))
        img = img.filter(GaussianBlur(self.blurRadius)
                         ).point(lambda x: int(x * 0.7))
        self.blurPix = img.toqpixmap()

        self.update()

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # 绘制磨砂背景
        if self.blurPix:
            r = self.__paintRadius
            dr = self.radius - r
            self.__drawCirclePic(painter, dr, dr, 2*r, 2*r, self.blurPix)

        # 绘制图标
        self.__drawCirclePic(painter, 5, 5, self.width()-10,
                             self.height() - 10, self.iconPix)

    def __drawCirclePic(self, painter, x, y, width, height, pixmap):
        """ 在指定区域画圆 """
        brush = QBrush(pixmap)
        painter.setBrush(brush)
        painter.drawEllipse(x, y, width, height)

    def enterEvent(self, e: QEnterEvent):
        """ 鼠标进入按钮时增大按钮并显示提示条 """
        if self.radiusAni.state() == QPropertyAnimation.Running:
            self.radiusAni.stop()

        # 显示工具提示
        super().enterEvent(e)

        self.radiusAni.setStartValue(self.__paintRadius)
        self.radiusAni.setEndValue(self.radius)
        self.radiusAni.setDuration(100)
        self.radiusAni.start()

    def leaveEvent(self, e):
        """ 鼠标离开按钮时减小按钮并隐藏提示条 """
        if self.radiusAni.state() == QPropertyAnimation.Running:
            self.radiusAni.stop()

        super().leaveEvent(e)

        self.radiusAni.setStartValue(self.__paintRadius)
        self.radiusAni.setEndValue(self.radius-5)
        self.radiusAni.setDuration(100)
        self.radiusAni.start()

    def setPaintRadius(self, radius: int):
        """ 设置绘制的半径 """
        self.__paintRadius = radius
        self.update()

    def getPaintRadius(self):
        return self.__paintRadius

    paintRadius = pyqtProperty(int, getPaintRadius, setPaintRadius)
