# coding:utf-8

import cv2 as cv
import numpy
from scipy.ndimage.filters import gaussian_filter
from PyQt5.QtGui import QImage, QPixmap


class BasicPerspectiveTransform():
    """ 透视变换基类 """

    def __init__(self, src=None):
        """ 实例化透视变换对象
        Parameter
        ---------
        src : numpy数组 """
        self.setSrc(src)

    def setSrc(self, src):
        """ 设置进行透视变换的源数组 """
        self.src = src
        if src is None:
            return
        self.height, self.width = self.src.shape[:2]
        # 变换前后的边角坐标
        self.srcPoints = numpy.float32(
            [[0, 0], [self.width - 1, 0], [0, self.height - 1],
             [self.width - 1, self.height - 1]])

    def setDstPoints(self, leftTop: list, rightTop, leftBottom, rightBottom):
        """ 设置变换后的边角坐标 """
        self.dstPoints = numpy.float32(
            [leftTop, rightTop, leftBottom, rightBottom])

    def getPerspectiveTransform(self, imWidth, imHeight, borderMode=cv.BORDER_CONSTANT, borderValue=[255, 255, 255, 0], isGetQPixmap: bool = False) -> QPixmap:
        """ 透视变换图像，返回QPixmap
        Parameters
        ----------
        imWidth : 变换后的图像宽度\n
        imHeight : 变换后的图像高度\n
        borderMode : 边框插值方式\n
        borderValue : 边框颜色\n
        isGetQPixmap : 是否返回QPixmap
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

        # 将ndarray转换为QPixmap，只有在创建了gui的情况下才能成功转换
        if isGetQPixmap:
            height, width, bytesPerComponent = self.dst.shape
            bytesPerLine = 4 * width
            dst = cv.cvtColor(self.dst, cv.COLOR_BGRA2RGBA)
            pix = QPixmap.fromImage(
                QImage(dst.data, width, height, bytesPerLine, QImage.Format_RGBA8888))
            return pix
        
    def show(self, imageNum=2):
        """ 显示图像 """
        if imageNum == 2:
            cv.imshow('before trans', self.src)
        cv.imshow('after tarns', self.dst)
        cv.waitKey()
        cv.destroyAllWindows()

    def save(self, savePath):
        """ 以png格式保存图像 """
        cv.imencode('.png', self.dst)[1].tofile(savePath)


class PerspectiveTransform(BasicPerspectiveTransform):
    """ 对图像进行透视变换 """

    def __init__(self, filePath, picSize: tuple = None):
        super().__init__()
        self.filePath = filePath
        self.pressedPos = None
        self.picSize = picSize
        # 读入数据
        self.__cvImread()

    def __cvImread(self):
        """ 读取图片数据 """
        # 如果是jpg返回BGR格式，如果是png返回BGRA
        self.setSrc(cv.imdecode(numpy.fromfile(
            self.filePath, dtype=numpy.uint8), -1))
        # 改变图片尺寸
        if self.picSize:
            self.setSrc(cv.resize(self.src, self.picSize))


class PixmapPerspectiveTransForm(BasicPerspectiveTransform):
    """ 对QPixmap进行透视变换 """

    def __init__(self, pixmap: QPixmap=None):
        super().__init__()
        self.pressedPos = None
        self.setPixmap(pixmap)

    def setPixmap(self, pixmap: QPixmap):
        """ 设置被变换的QPixmap """
        self.pixmap = QPixmap
        if not pixmap:
            return
        # 获取图像的尺寸
        self.width, self.height = pixmap.width(), pixmap.height()
        channels_count = 4
        image = pixmap.toImage()  # type:QImage
        b = image.bits()
        b.setsize(self.height * self.width * channels_count)
        self.setSrc(numpy.frombuffer(b, numpy.uint8).reshape(
            (self.height, self.width, channels_count)))


if __name__ == '__main__':

    trans = PerspectiveTransform(
        'resource\\Album_Cover\\オーダーメイド\\オーダーメイド.jpg', (200, 200))
    trans.setDstPoints(
        [2, 0], [trans.width-3, 3], [1, trans.height-2], [trans.width-5, trans.height-3])
    trans.getPerspectiveTransform(trans.width, trans.height)
    trans.show()
    trans.save('test.png')
