# coding:utf-8
import cv2 as cv
import numpy as np
from PyQt5.QtGui import QImage, QPixmap


class PixmapPerspectiveTransform():
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

    def transNdarrayToQPixmap(self, array:np.ndarray):
        """ 将numpy数组转换为QPixmap """
        height, width, bytesPerComponent = array.shape
        bytesPerLine = 4 * width
        # 默认数组维度为 m*n*4
        dst = cv.cvtColor(array, cv.COLOR_BGRA2RGBA)
        pix = QPixmap.fromImage(
            QImage(dst.data, width, height, bytesPerLine, QImage.Format_RGBA8888))
        return pix
