# coding:utf-8
from PIL import Image, ImageDraw
from PIL.ImageFilter import GaussianBlur
from PIL.ImageQt import ImageQt

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget


class SingerBlurBackground(QWidget):
    """ Blur background under singer card """

    def __init__(self, parent=None, imagePath: str = '', imageSize: tuple = (210, 210), blurRadius=30):
        """
        Parameters
        ----------
        parent:
            parent window

        imagePath: str
            singer avatar path

        imageSize: tuple
            image size after adjusting

        blurRadius: int
            blur radius
        """
        super().__init__(parent)
        self.__blurImage = None
        self.setBlurAlbum(imagePath, imageSize, blurRadius)

    def setBlurAlbum(self, imagePath: str, imageSize: tuple = (210, 210), blurRadius=30):
        """ set the album cover to be blurred """
        if not imagePath:
            return

        if not imagePath.startswith(':'):
            avatar = Image.open(imagePath)
        else:
            avatar = Image.fromqpixmap(QPixmap(imagePath))

        avatar = avatar.resize(imageSize)
        self.__blurRadius = blurRadius

        # create a new image
        blurAvatar = Image.new(
            'RGBA', (imageSize[0]+2*blurRadius, imageSize[1]+2*blurRadius), (0, 0, 0, 0))
        mask = Image.new('L', imageSize, 0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice([(0, 0), imageSize], 0, 360, fill=255)
        blurAvatar.paste(avatar, (blurRadius, blurRadius), mask)

        # apply Gaussian blur to album cover
        blurAvatar = blurAvatar.filter(GaussianBlur(blurRadius/2))
        self.__blurImage = ImageQt(blurAvatar)

        self.resize(*blurAvatar.size)
        self.update()

    def setBlurRadius(self, blurRadius):
        """ set blur radius """
        self.__blurRadius = blurRadius

    def paintEvent(self, e):
        """ paint blurred album cover """
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
