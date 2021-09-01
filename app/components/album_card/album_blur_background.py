# coding:utf-8

from PIL import Image
from PIL.ImageFilter import GaussianBlur
from PIL.ImageQt import ImageQt

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget


class AlbumBlurBackground(QWidget):
    """ 专辑卡磨砂背景 """

    def __init__(self, parent=None, imagePath: str = '', imageSize: tuple = (210, 210), blurRadius=30):
        """
        Parameters
        ----------
        parent:
            父级窗口
        imagePath: str
            专辑封面路径

        imageSize: tuple
            调整大小后的图片尺寸

        blurRadius: int
            磨砂半径, 磨砂后的图片尺寸将等于磨砂半径*2加上宽和高 """
        super().__init__(parent)
        self.__blurImage = None
        self.setBlurAlbum(imagePath, imageSize, blurRadius)

    def setBlurAlbum(self, imagePath: str, imageSize: tuple = (210, 210), blurRadius=30):
        """ 更新磨砂专辑封面 """
        self.__blurRadius = blurRadius
        if not imagePath:
            return

        if not imagePath.startswith(':'):
            albumCover = Image.open(imagePath)
        else:
            albumCover=Image.fromqpixmap(QPixmap(imagePath))

        albumCover = albumCover.resize(imageSize)

        # 创建一个新图像
        blurAlbumCover = Image.new(
            'RGBA', (imageSize[0]+2*blurRadius, imageSize[1]+2*blurRadius), (255, 255, 255, 0))
        blurAlbumCover.paste(albumCover, (blurRadius, blurRadius))

        # 对图像进行高斯模糊
        blurAlbumCover = blurAlbumCover.filter(GaussianBlur(blurRadius/2))
        self.__blurImage = ImageQt(blurAlbumCover)

        self.resize(*blurAlbumCover.size)
        self.update()

    def setBlurRadius(self, blurRadius):
        """ 设置磨砂半径 """
        self.__blurRadius = blurRadius

    def paintEvent(self, e):
        """ 绘制磨砂图 """
        super().paintEvent(e)
        if not self.__blurImage:
            return
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        painter.drawImage(0, 0, self.__blurImage)

    @property
    def blurRadius(self):
        return self.__blurRadius