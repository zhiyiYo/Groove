# coding:utf-8
import imghdr
from math import floor
from io import BytesIO
from typing import Union

import cv2 as cv
import numpy as np
from colorthief import ColorThief
from PIL import Image
from PyQt5.QtCore import QIODevice, QBuffer
from PyQt5.QtGui import QImage, QPixmap
from scipy.ndimage.filters import gaussian_filter

from .exception_handler import exceptionHandler
from .logger import Logger


def readImage(imagePath: str):
    """ read image

    Parameters
    ----------
    imagePath: str
        image file path

    Returns
    -------
    image: `~PIL.Image`
        image instance
    """
    try:
        if not imagePath.startswith(':'):
            return Image.open(imagePath)
    except Exception as e:
        Logger("image").error(e)
        imagePath = ":/images/default_covers/album_200_200.png"

    return fromqpixmap(QPixmap(imagePath))


def fromqpixmap(im: Union[QImage, QPixmap]):
    """
    :param im: QImage or PIL ImageQt object
    """
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)

    # preserve alpha channel with png
    # otherwise ppm is more friendly with Image.open
    if im.hasAlphaChannel():
        im.save(buffer, "png")
    else:
        im.save(buffer, "ppm")

    b = BytesIO()
    b.write(buffer.data())
    buffer.close()
    b.seek(0)

    return Image.open(b)


def gaussianBlur(imagePath: str, blurRadius=18, brightFactor=1, blurPicSize: tuple = None) -> np.ndarray:
    """ apply Gaussian blur to image

    Parameters
    ----------
    imagePath: str
        the image to be blurred

    blurRadius: int
        blur radius

    brightFactor: float
        brightness scale factor

    blurPicSize: tuple
        the maximum size of image, if the actual picture exceeds this size,
        it will be scaled to speed up the computation speed.

    Returns
    -------
    image: `~np.ndarray` of shape `(w, h, c)`
        the image after blurring
    """
    image = readImage(imagePath)

    if blurPicSize:
        # scale image to speed up the computation speed
        w, h = image.size
        ratio = min(blurPicSize[0] / w, blurPicSize[1] / h)
        w_, h_ = w * ratio, h * ratio

        if w_ < w:
            if hasattr(Image, 'ANTIALIAS'):
                image = image.resize((int(w_), int(h_)), Image.ANTIALIAS)
            else:
                image = image.resize((int(w_), int(h_)), Image.Resampling.BILINEAR)


    image = np.array(image)

    # handle gray image
    if len(image.shape) == 2:
        image = np.stack([image, image, image], axis=-1)

    # blur each color channel
    for i in range(3):
        image[:, :, i] = gaussian_filter(
            image[:, :, i], blurRadius) * brightFactor

    return image


def getBlurPixmap(imagePath: str, blurRadius=30, brightFactor=1, blurPicSize: tuple = None) -> QPixmap:
    """ apply Gaussian blur to image

    Parameters
    ----------
    imagePath: str
        the image to be blurred

    blurRadius: int
        blur radius

    brightnessFactor: float
        brightness scale factor

    blurPicSize: tuple
        the maximum size of image, if the actual picture exceeds this size,
        it will be scaled to speed up the computation speed.

    Returns
    -------
    blurPixmap: QPixmap
        the image after blurring
    """
    image = gaussianBlur(imagePath, blurRadius, brightFactor, blurPicSize)
    return imageToQPixmap(image)


def imageToQPixmap(image):
    if isinstance(image, Image.Image):
        image = np.uint8(image)

    h, w, c = image.shape
    if c == 3:
        format = QImage.Format_RGB888
    else:
        format = QImage.Format_RGBA8888

    return QPixmap.fromImage(QImage(image.data, w, h, c*w, format))


class DominantColor:
    """ Dominant color class """

    @classmethod
    @exceptionHandler("image", (24, 24, 24))
    def getDominantColor(cls, imagePath: str):
        """ extract dominant color from image

        Parameters
        ----------
        imagePath: str
            image path

        Returns
        -------
        r, g, b: int
            gray value of each color channel
        """
        if imagePath.startswith(':'):
            return (24, 24, 24)

        colorThief = ColorThief(imagePath)

        # scale image to speed up the computation speed
        if max(colorThief.image.size) > 400:
            colorThief.image = colorThief.image.resize((400, 400))

        palette = colorThief.get_palette(quality=9)

        # adjust the brightness of palette
        palette = cls.__adjustPaletteValue(palette)
        for rgb in palette[:]:
            h, s, v = cls.rgb2hsv(rgb)
            if h < 0.02:
                palette.remove(rgb)
                if len(palette) <= 2:
                    break

        palette = palette[:5]
        palette.sort(key=lambda rgb: cls.colorfulness(*rgb), reverse=True)

        return palette[0]

    @classmethod
    def __adjustPaletteValue(cls, palette: list):
        """ adjust the brightness of palette """
        newPalette = []
        for rgb in palette:
            h, s, v = cls.rgb2hsv(rgb)
            if v > 0.9:
                factor = 0.8
            elif 0.8 < v <= 0.9:
                factor = 0.9
            elif 0.7 < v <= 0.8:
                factor = 0.95
            else:
                factor = 1
            v *= factor
            newPalette.append(cls.hsv2rgb(h, s, v))

        return newPalette

    @staticmethod
    def rgb2hsv(rgb: tuple) -> tuple:
        """ convert rgb to hsv """
        r, g, b = [i / 255 for i in rgb]
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360
        s = 0 if mx == 0 else df / mx
        v = mx
        return (h, s, v)

    @staticmethod
    def hsv2rgb(h, s, v) -> tuple:
        """ convert hsv to rgb """
        h60 = h / 60.0
        h60f = floor(h60)
        hi = int(h60f) % 6
        f = h60 - h60f
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        r, g, b = 0, 0, 0
        if hi == 0:
            r, g, b = v, t, p
        elif hi == 1:
            r, g, b = q, v, p
        elif hi == 2:
            r, g, b = p, v, t
        elif hi == 3:
            r, g, b = p, q, v
        elif hi == 4:
            r, g, b = t, p, v
        elif hi == 5:
            r, g, b = v, p, q
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return (r, g, b)

    @staticmethod
    def colorfulness(r: int, g: int, b: int):
        rg = np.absolute(r - g)
        yb = np.absolute(0.5 * (r + g) - b)

        # Compute the mean and standard deviation of both `rg` and `yb`.
        rg_mean, rg_std = (np.mean(rg), np.std(rg))
        yb_mean, yb_std = (np.mean(yb), np.std(yb))

        # Combine the mean and standard deviations.
        std_root = np.sqrt((rg_std ** 2) + (yb_std ** 2))
        mean_root = np.sqrt((rg_mean ** 2) + (yb_mean ** 2))

        return std_root + (0.3 * mean_root)


def getPicSuffix(pic_data: bytes) -> str:
    """ determine the suffix of binary image data """
    try:
        suffix = '.' + imghdr.what(None, pic_data)
        if suffix == '.jpeg':
            suffix = '.jpg'
    except:
        suffix = '.jpg'

    return suffix


def getPicMimeType(pic_data: bytes) -> str:
    """ determine the mime type of binary image data """
    try:
        mimeType = "image/" + imghdr.what(None, pic_data)
    except:
        mimeType = "image/jpeg"

    return mimeType


class PixmapPerspectiveTransform:
    """ Pixmap perspective transform class """

    def __init__(self, pixmap=None):
        self.pixmap = pixmap

    def setPixmap(self, pixmap: QPixmap):
        """ set the image to be transformed """
        self.pixmap = QPixmap
        self.src = self.transQPixmapToNdarray(pixmap)
        self.height, self.width = self.src.shape[:2]

        # corner coordinates before transformation
        self.srcPoints = np.float32(
            [[0, 0], [self.width - 1, 0], [0, self.height - 1],
             [self.width - 1, self.height - 1]])

    def setDstPoints(self, leftTop: list, rightTop, leftBottom, rightBottom):
        """ set the corner coordinates after transformation """
        self.dstPoints = np.float32(
            [leftTop, rightTop, leftBottom, rightBottom])

    def getPerspectiveTransform(self, imWidth: int, imHeight: int, borderMode=cv.BORDER_CONSTANT, borderValue=[255, 255, 255, 0]) -> QPixmap:
        """ get transformed image

        Parameters
        ----------
        imWidth: int
            image width before transformation

        imHeight: int
            image height before transformation

        borderMode: int
            border interpolation mode

        borderValue: list
            filled border color

        Returns
        -------
        pixmap: QPixmap
            image after transformation
        """
        # handle jpeg image
        if self.src.shape[-1] == 3:
            self.src = cv.cvtColor(self.src, cv.COLOR_BGR2BGRA)

        # calculate transform matrix
        perspectiveMatrix = cv.getPerspectiveTransform(
            self.srcPoints, self.dstPoints)

        # apply perspective transform
        self.dst = cv.warpPerspective(self.src, perspectiveMatrix, (
            imWidth, imHeight), borderMode=borderMode, borderValue=borderValue)

        return self.transNdarrayToQPixmap(self.dst)

    def transQPixmapToNdarray(self, pixmap: QPixmap):
        """ 将QPixmap转换为numpy数组 """
        width, height = pixmap.width(), pixmap.height()
        channels_count = 4
        image = pixmap.toImage()  # type:QImage
        s = image.bits().asstring(height * width * channels_count)

        # BGRA image array
        array = np.fromstring(s, np.uint8).reshape(
            (height, width, channels_count))

        return array

    def transNdarrayToQPixmap(self, array: np.ndarray):
        """ convert numpy array to QPixmap """
        height, width, bytesPerComponent = array.shape
        bytesPerLine = 4 * width

        # array shape: m*n*4
        dst = cv.cvtColor(array, cv.COLOR_BGRA2RGBA)
        pix = QPixmap.fromImage(
            QImage(dst.data, width, height, bytesPerLine, QImage.Format_RGBA8888))
        return pix
