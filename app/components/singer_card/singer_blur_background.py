# coding:utf-8
from common.config import config, Theme
from common.image_utils import readImage, imageToQPixmap
from components.widgets.label import FadeInLabel
from PIL import Image, ImageDraw
from PIL.ImageFilter import GaussianBlur


class SingerBlurBackground(FadeInLabel):
    """ Blur background under singer card """

    def __init__(self, parent=None, imagePath: str = '', imageSize: tuple = (210, 210), blurRadius=5):
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
        self.setBlurAvatar(imagePath, imageSize, blurRadius)

    def setBlurAvatar(self, imagePath: str, imageSize: tuple = (200, 200), blurRadius=30):
        """ set the avatar to be blurred """
        if not imagePath:
            return

        avatar = readImage(imagePath).resize(imageSize)

        # create a new image
        r = 0 if config.theme == Theme.DARK else 255
        blurAvatar = Image.new(
            'RGBA', (imageSize[0]+2*blurRadius, imageSize[1]+2*blurRadius), (r, r, r, 0))
        mask = Image.new('L', imageSize, 0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice([(0, 0), imageSize], 0, 360, fill=255)
        blurAvatar.paste(avatar, (blurRadius, blurRadius), mask)

        # apply Gaussian blur to album cover
        blurAvatar = blurAvatar.filter(GaussianBlur(blurRadius/2))
        self.resize(*blurAvatar.size)
        self.setPixmap(imageToQPixmap(blurAvatar))

    def showEvent(self, e):
        super().showEvent(e)
        self.ani.setStartValue(0)
        self.ani.setEndValue(1)
        self.ani.setDuration(120)
        self.ani.start()
