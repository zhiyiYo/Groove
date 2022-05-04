# coding:utf-8
from components.widgets.label import FadeInLabel
from PIL import Image
from PIL.ImageFilter import GaussianBlur
from PyQt5.QtGui import QPixmap


class AlbumBlurBackground(FadeInLabel):
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
        self.setBlurAlbum(imagePath, imageSize, blurRadius)

    def setBlurAlbum(self, imagePath: str, imageSize: tuple = (210, 210), blurRadius=30):
        """ set the album cover to be blurred """
        if not imagePath:
            return

        if not imagePath.startswith(':'):
            albumCover = Image.open(imagePath)
        else:
            albumCover = Image.fromqpixmap(QPixmap(imagePath))

        albumCover = albumCover.resize(imageSize)

        # create a new image
        blurAlbumCover = Image.new(
            'RGBA', (imageSize[0]+2*blurRadius, imageSize[1]+2*blurRadius), (255, 255, 255, 0))
        blurAlbumCover.paste(albumCover, (blurRadius, blurRadius))

        # apply Gaussian blur to album cover
        blurAlbumCover = blurAlbumCover.filter(GaussianBlur(blurRadius/2))
        self.resize(*blurAlbumCover.size)
        self.setPixmap(blurAlbumCover.toqpixmap())

    def showEvent(self, e):
        super().showEvent(e)
        self.ani.setStartValue(0)
        self.ani.setEndValue(1)
        self.ani.setDuration(110)
        self.ani.start()
