# coding:utf-8
from common.icon import drawSvgIcon
from PIL.ImageFilter import GaussianBlur
from PyQt5.QtCore import QPropertyAnimation, Qt, pyqtProperty, QRectF, QSize
from PyQt5.QtGui import QBrush, QEnterEvent, QPainter, QPixmap, QImage

from .tool_tip_button import ToolTipButton
from common.image_utils import readImage, imageToQPixmap


class BlurButton(ToolTipButton):
    """ Blur button class """

    def __init__(self, parent, cropPos: tuple, iconPath: str, blurPicPath: str,
                 text: str, radius=35, blurRadius=40, iconSize=(25, 25)):
        """
        Parameters
        ----------
        parent:
            parent window

        cropPos: tuple
            coordinates of the image cropping position

        iconPath: str
            icon path

        blurPicPath: str
            image to be blurred

        text: str
            text of tool tip

        radius: int
            button radius

        blurRadius: int
            blur radius

        iconSize: tuple
            icon size
        """
        super().__init__(parent=parent)
        self.__paintRadius = radius-5
        self.__opacity = 0
        self.radius = radius
        self.resize(radius*2, radius*2)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setIconSize(QSize(*iconSize))

        self.blurPix = None
        self.blurPicPath = blurPicPath
        self.blurRadius = blurRadius
        self.cropX, self.cropY = cropPos
        self.iconPath = iconPath
        self.radiusAni = QPropertyAnimation(self, b'paintRadius', self)
        self.opacityAni = QPropertyAnimation(self, b'opacity', self)
        self.setToolTip(text)
        self.setToolTipDelay(250)

    def setBlurPic(self, blurPicPath, blurRadius=35):
        """ set the image to be blurred """
        if self.blurPicPath == blurPicPath:
            return

        self.blurPicPath = blurPicPath
        self.blurRadius = blurRadius
        self.blurPix = None

    def __blur(self):
        """ do blur action """
        img = readImage(self.blurPicPath).convert('RGB').resize((200, 200))
        img = img.crop((
            self.cropX,
            self.cropY,
            self.width() + self.cropX,
            self.height() + self.cropY
        ))
        img = img.filter(GaussianBlur(self.blurRadius)).point(lambda x: int(x * 0.7))
        self.blurPix = imageToQPixmap(img)
        self.update()

    def fadeIn(self):
        """ fade in """
        self.__opacity = 0
        super().show()
        self.opacityAni.setStartValue(0)
        self.opacityAni.setEndValue(1)
        self.opacityAni.setDuration(110)
        self.opacityAni.start()

    def showEvent(self, e):
        if not self.blurPix:
            self.__blur()

        self.__paintRadius = self.radius-5
        self.__opacity = 1
        super().showEvent(e)

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setOpacity(self.__opacity)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # draw background
        if self.blurPix:
            r = self.__paintRadius
            dr = self.radius - r
            self.__drawCirclePic(painter, dr, dr, 2*r, 2*r, self.blurPix)

        # draw icon
        iw, ih = self.iconSize().width(), self.iconSize().height()
        rect = QRectF((self.width()-iw)/2, (self.height()-ih)/2, iw, ih)
        drawSvgIcon(self.iconPath, painter, rect)

    def __drawCirclePic(self, painter, x, y, width, height, pixmap):
        """ paint image in circle region """
        brush = QBrush(pixmap)
        painter.setBrush(brush)
        painter.drawEllipse(x, y, width, height)

    def enterEvent(self, e: QEnterEvent):
        if self.radiusAni.state() == QPropertyAnimation.Running:
            self.radiusAni.stop()

        super().enterEvent(e)

        self.radiusAni.setStartValue(self.__paintRadius)
        self.radiusAni.setEndValue(self.radius)
        self.radiusAni.setDuration(100)
        self.radiusAni.start()

    def leaveEvent(self, e):
        if self.radiusAni.state() == QPropertyAnimation.Running:
            self.radiusAni.stop()

        super().leaveEvent(e)

        self.radiusAni.setStartValue(self.__paintRadius)
        self.radiusAni.setEndValue(self.radius-5)
        self.radiusAni.setDuration(100)
        self.radiusAni.start()

    def setPaintRadius(self, radius: int):
        """ set the smallest radius of button """
        self.__paintRadius = radius
        self.update()

    def getPaintRadius(self):
        return self.__paintRadius

    def getOpacity(self):
        return self.__opacity

    def setOpacity(self, opacity: float):
        self.__opacity = opacity
        self.update()

    paintRadius = pyqtProperty(int, getPaintRadius, setPaintRadius)
    opacity = pyqtProperty(float, getOpacity, setOpacity)
