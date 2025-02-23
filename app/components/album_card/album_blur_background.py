# coding:utf-8
from common.config import config, Theme
from common.image_utils import readImage, imageToQPixmap
from components.widgets.label import FadeInLabel
from PIL import Image
from PIL.ImageFilter import GaussianBlur


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

        albumCover = readImage(imagePath).resize(imageSize)

        # create a new image
        r = 0 if config.theme == Theme.DARK else 255
        blurAlbumCover = Image.new(
            'RGBA', (imageSize[0]+2*blurRadius, imageSize[1]+2*blurRadius), (r, r, r, 0))
        blurAlbumCover.paste(albumCover, (blurRadius, blurRadius))

        # apply Gaussian blur to album cover
        blurAlbumCover = blurAlbumCover.filter(GaussianBlur(blurRadius/2))
        self.resize(*blurAlbumCover.size)
        self.setPixmap(imageToQPixmap(blurAlbumCover))

    def showEvent(self, e):
        super().showEvent(e)
        self.ani.setStartValue(0)
        self.ani.setEndValue(1)
        self.ani.setDuration(110)
        self.ani.start()
