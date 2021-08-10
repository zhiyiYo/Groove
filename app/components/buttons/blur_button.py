# coding:utf-8
from PIL import Image
from PIL.ImageFilter import GaussianBlur
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QEnterEvent, QPainter, QPixmap
from PyQt5.QtWidgets import QToolButton


class BlurButton(QToolButton):
    """ 磨砂按钮 """

    def __init__(self, parent, cropPos: tuple, iconPath: str, blurPicPath: str, buttonSize: tuple = (70, 70), blurRadius=40):
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

        buttonSize: tuple
            按钮大小

        blurRadius: int
            磨砂半径
        """
        super().__init__(parent=parent)
        self.resize(*buttonSize)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.blurPicPath = blurPicPath
        self.blurRadius = blurRadius
        self.cropX, self.cropY = cropPos
        self.iconPix = QPixmap(iconPath).scaled(
            *buttonSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.blurPix = None
        self.isEnter = False
        # 不马上磨砂，只在出现时磨砂
        # self.setBlurPic(blurPicPath, blurRadius)

    def showEvent(self, e) -> None:
        if not self.blurPix:
            self.__blur()
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
        img = Image.open(self.blurPicPath).convert('RGB').resize((200, 200))
        img = img.crop((self.cropX, self.cropY,
                        self.width() + self.cropX, self.height() + self.cropY))
        img = img.filter(GaussianBlur(self.blurRadius)
                         ).point(lambda x: int(x * 0.7))
        self.blurPix = img.toqpixmap()
        self.update()

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        # 绘制磨砂背景和图标
        if not self.isEnter:
            if self.blurPix:
                self.__drawCirclePic(painter, 5, 5, self.width()-10,
                                     self.height() - 10, self.blurPix)
            self.__drawCirclePic(painter, 5, 5, self.width()-10,
                                 self.height() - 10, self.iconPix)
        else:
            if self.blurPix:
                self.__drawCirclePic(
                    painter, 0, 0, self.width(), self.height(), self.blurPix)
            self.__drawCirclePic(painter, 5, 5, self.width()-10,
                                 self.height() - 10, self.iconPix)

    def __drawCirclePic(self, painter, x, y, width, height, pixmap):
        """ 在指定区域画圆 """
        brush = QBrush(pixmap)
        painter.setBrush(brush)
        painter.drawEllipse(x, y, width, height)

    def enterEvent(self, e: QEnterEvent):
        """ 鼠标进入按钮时增大按钮并显示提示条 """
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        """ 鼠标离开按钮时减小按钮并隐藏提示条 """
        self.isEnter = False
        self.update()
