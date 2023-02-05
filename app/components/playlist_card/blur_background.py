# coding:utf-8
from common.config import config, Theme
from common.image_utils import readImage
from components.widgets.label import FadeInLabel
from PIL import Image
from PIL.ImageFilter import GaussianBlur


class BlurBackground(FadeInLabel):
    """ Blur background under playlist card """

    def __init__(self, parent=None, imagePath: str = '', blurRadius=30):
        super().__init__(parent)
        self.setBlurPic(imagePath, blurRadius)

    def setBlurPic(self, imagePath: str, blurRadius: int = 30):
        """ set the cover to be blurred """
        if not imagePath:
            return

        # read album cover
        cover = readImage(imagePath).resize((288, 288)).crop((0, 92, 288, 288))

        # create a new image
        r = 0 if config.theme == Theme.DARK else 255
        blurImage = Image.new(
            'RGBA', (288 + 2 * blurRadius, 196 + 2 * blurRadius), (r, r, r, 0))
        blurImage.paste(cover, (blurRadius, blurRadius))

        # apply Gaussian blur to image
        blurImage = blurImage.filter(GaussianBlur(blurRadius/2))
        self.resize(*blurImage.size)
        self.setPixmap(blurImage.toqpixmap())

    def showEvent(self, e):
        super().showEvent(e)
        self.ani.setStartValue(0)
        self.ani.setEndValue(1)
        self.ani.setDuration(110)
        self.ani.start()
