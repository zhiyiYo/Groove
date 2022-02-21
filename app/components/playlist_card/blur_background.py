# coding:utf-8
from PIL import Image
from PIL.ImageFilter import GaussianBlur
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget


class BlurBackground(QWidget):
    """ Blur background under playlist card """

    def __init__(self, parent=None, imagePath: str = '', blurRadius=30):
        super().__init__(parent)
        self.__blurPix = None
        self.setBlurPic(imagePath, blurRadius)

    def setBlurPic(self, imagePath: str, blurRadius: int = 30):
        """ set the cover to be blurred """
        if not imagePath:
            return

        # read album cover
        if not imagePath.startswith(':'):
            cover = Image.open(imagePath)
        else:
            cover = Image.fromqpixmap(QPixmap(imagePath))

        cover = cover.resize((288, 288)).crop((0, 92, 288, 288))

        # create a new image
        blurImage = Image.new(
            'RGBA', (288 + 2 * blurRadius, 196 + 2 * blurRadius), (255, 255, 255, 0))
        blurImage.paste(cover, (blurRadius, blurRadius))

        # apply Gaussian blur to image
        blurImage = blurImage.filter(GaussianBlur(blurRadius/2))
        self.__blurPix = blurImage.toqpixmap()

        self.resize(*blurImage.size)
        self.update()

    def paintEvent(self, e):
        """ paint blur background """
        super().paintEvent(e)
        if not self.__blurPix:
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        painter.drawPixmap(0, 0, self.__blurPix)
