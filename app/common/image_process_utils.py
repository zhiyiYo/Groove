# coding:utf-8
import imghdr
from math import floor

import cv2 as cv
import numpy as np
from colorthief import ColorThief
from PIL import Image
from PyQt5.QtGui import QImage, QPixmap
from scipy.ndimage.filters import gaussian_filter


def gaussianBlur(imagePath: str, savePath='', blurRadius=18, brightnessFactor=1, blurPicSize: tuple = None) -> np.ndarray:
    """ 对图片进行高斯模糊处理

    Parameters
    ----------
    imagePath: str
        图片路径

    savePath: str
        保存路径

    blurRadius: int
        模糊半径

    brightnessFactor：float
        亮度缩放因子

    blurPicSize: tuple
        高斯模糊前将图片缩放到指定大小，可以加快模糊速度

    Returns
    -------
    blurImageArray: `~np.ndarray`
        高斯模糊后的图像数组
    """
    if not imagePath.startswith(':'):
        image = Image.open(imagePath)
    else:
        image = Image.fromqpixmap(QPixmap(imagePath))

    if blurPicSize:
        # 调整图片尺寸，减小计算量，还能增加额外的模糊(手动滑稽)
        oldWidth, oldHeight = image.size
        ratio = min(blurPicSize[0] / oldWidth, blurPicSize[1] / oldHeight)
        newWidth, newHeight = oldWidth * ratio, oldHeight * ratio

        # 如果新的尺寸小于旧尺寸才 resize
        if newWidth < oldWidth:
            imageArray = np.array(image.resize(
                (int(newWidth), int(newHeight)), Image.ANTIALIAS))
        else:
            imageArray = np.array(image)
    else:
        imageArray = np.array(image)

    blurImageArray = imageArray

    # 对每一个颜色通道分别磨砂
    for i in range(imageArray.shape[-1]):
        blurImageArray[:, :, i] = gaussian_filter(
            imageArray[:, :, i], blurRadius) * brightnessFactor

    # 将ndarray转换为Image对象
    if savePath:
        blurImage = Image.fromarray(blurImageArray)
        blurImage.save(savePath)
    return blurImageArray


def getBlurPixmap(imagePath, blurRadius=30, brightnessFactor=1, blurPicSize: tuple = None) -> QPixmap:
    """ 对原图进行高斯模糊处理

    Parameters
    ----------
    imagePath: str
        图片路径

    blurRadius: int
        模糊半径

    brightnessFactor：float
        亮度缩放因子

    blurPicSize: tuple
        高斯模糊前将图片缩放到指定大小，可以加快模糊速度

    Returns
    -------
    blurPixmap: QPixmap
        高斯模糊后的图像
    """
    blurArray = gaussianBlur(
        imagePath, blurRadius=blurRadius, brightnessFactor=brightnessFactor, blurPicSize=blurPicSize)
    height, width, bytesPerComponent = blurArray.shape
    bytesPerLine = bytesPerComponent * width  # 每行的字节数
    # 设置转换格式
    if blurArray.shape[-1] == 4:
        imageFormat = QImage.Format_RGBA8888
    else:
        imageFormat = QImage.Format_RGB888
    # 将ndarray转换为QPixmap
    blurPixmap = QPixmap.fromImage(
        QImage(blurArray.data, width, height, bytesPerLine, imageFormat))
    return blurPixmap


class DominantColor:
    """ 获取图像的主色调 """

    @classmethod
    def getDominantColor(cls, imagePath: str):
        """ 获取指定图片的主色调

        Parameters
        ----------
        imagePath: str
            图片路径
        """
        if imagePath.startswith(':'):
            return (24, 24, 24)

        colorThief = ColorThief(imagePath)

        # 调整图像大小，加快运算速度
        if max(colorThief.image.size) > 400:
            colorThief.image = colorThief.image.resize((400, 400))

        palette = colorThief.get_palette(quality=9)

        # 调整调色板明度
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
        """ 调整调色板的明度 """
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
        """ rgb空间变换到hsv空间 """
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
        """ hsv空间变换到rgb空间 """
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


def getPicSuffix(pic_data) -> str:
    """ 获取二进制图片数据的后缀名 """
    try:
        suffix = '.' + imghdr.what(None, pic_data)
        if suffix == '.jpeg':
            suffix = '.jpg'
    except:
        suffix = '.jpg'
    return suffix


class PixmapPerspectiveTransform:
    """ 透视变换基类 """

    def __init__(self, pixmap=None):
        self.pixmap = pixmap

    def setPixmap(self, pixmap: QPixmap):
        """ 设置被变换的QPixmap """
        self.pixmap = QPixmap
        self.src = self.transQPixmapToNdarray(pixmap)
        self.height, self.width = self.src.shape[:2]
        # 变换前后的边角坐标
        self.srcPoints = np.float32(
            [[0, 0], [self.width - 1, 0], [0, self.height - 1],
             [self.width - 1, self.height - 1]])

    def setDstPoints(self, leftTop: list, rightTop, leftBottom, rightBottom):
        """ 设置变换后的边角坐标 """
        self.dstPoints = np.float32(
            [leftTop, rightTop, leftBottom, rightBottom])

    def getPerspectiveTransform(self, imWidth: int, imHeight: int, borderMode=cv.BORDER_CONSTANT, borderValue=[255, 255, 255, 0]) -> QPixmap:
        """ 透视变换图像

        Parameters
        ----------
        imWidth: int
            变换后的图像宽度

        imHeight: int
            变换后的图像高度

        borderMode: int
            边框插值方式

        borderValue: list
            边框颜色
        """
        # 如果是jpg需要加上一个透明通道
        if self.src.shape[-1] == 3:
            self.src = cv.cvtColor(self.src, cv.COLOR_BGR2BGRA)
        # 透视变换矩阵
        perspectiveMatrix = cv.getPerspectiveTransform(
            self.srcPoints, self.dstPoints)
        # 执行变换
        self.dst = cv.warpPerspective(self.src, perspectiveMatrix, (
            imWidth, imHeight), borderMode=borderMode, borderValue=borderValue)
        # 将ndarray转换为QPixmap
        return self.transNdarrayToQPixmap(self.dst)

    def transQPixmapToNdarray(self, pixmap: QPixmap):
        """ 将QPixmap转换为numpy数组 """
        width, height = pixmap.width(), pixmap.height()
        channels_count = 4
        image = pixmap.toImage()  # type:QImage
        s = image.bits().asstring(height * width * channels_count)
        # 得到BGRA格式数组
        array = np.fromstring(s, np.uint8).reshape(
            (height, width, channels_count))
        return array

    def transNdarrayToQPixmap(self, array: np.ndarray):
        """ 将numpy数组转换为QPixmap """
        height, width, bytesPerComponent = array.shape
        bytesPerLine = 4 * width
        # 默认数组维度为 m*n*4
        dst = cv.cvtColor(array, cv.COLOR_BGRA2RGBA)
        pix = QPixmap.fromImage(
            QImage(dst.data, width, height, bytesPerLine, QImage.Format_RGBA8888))
        return pix
