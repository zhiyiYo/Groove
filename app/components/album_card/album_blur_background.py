# coding:utf-8

from PIL import Image
from PIL.ImageFilter import GaussianBlur
from PIL.ImageQt import ImageQt

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget


class AlbumBlurBackground(QWidget):
    """ Blur background under album card """

    def __init__(self, parent=None, imagePath: str = '', imageSize: tuple = (210, 210), blurRadius=30):
        """
        Parameters
        ----------
        parent:
            parent window

        imagePath: str
            album cover path

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
        self.__blurRadius = blurRadius
        if not imagePath:
            return

        if not imagePath.startswith(':'):
            albumCover = Image.open(imagePath)
        else:
            albumCover=Image.fromqpixmap(QPixmap(imagePath))

        albumCover = albumCover.resize(imageSize)

        # create a new image
        blurAlbumCover = Image.new(
            'RGBA', (imageSize[0]+2*blurRadius, imageSize[1]+2*blurRadius), (255, 255, 255, 0))
        blurAlbumCover.paste(albumCover, (blurRadius, blurRadius))

        # apply Gaussian blur to album cover
        blurAlbumCover = blurAlbumCover.filter(GaussianBlur(blurRadius/2))
        self.__blurImage = ImageQt(blurAlbumCover)

        self.resize(*blurAlbumCover.size)
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