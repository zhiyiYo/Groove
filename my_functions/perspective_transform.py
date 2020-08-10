import cv2 as cv
import numpy
from PyQt5.QtGui import QImage, QPixmap


class PerspectiveTransform():
    """ 透视变换 """

    def __init__(self, filePath,picSize:tuple=None):
        self.filePath = filePath
        self.width = 0
        self.height = 0
        self.pressedPos = None
        self.picSize = picSize
        # 读入数据
        self.__cvImread()
        # 变换前后的边角坐标
        self.srcPoints = numpy.float32(
            [[0, 0], [self.width - 1, 0], [0, self.height - 1],
             [self.width - 1, self.height - 1]])

    def __cvImread(self):
        """ 读取图片数据 """
        # 如果是jpg返回BGR格式，如果是png返回BGRA
        self.src = cv.imdecode(numpy.fromfile(
            self.filePath, dtype=numpy.uint8), -1)
        # 改变图片尺寸
        if self.picSize:
            self.src = cv.resize(self.src, self.picSize)
        self.height, self.width = self.src.shape[:2]

    def setDstPoints(self, leftTop: list, rightTop, leftBottom, rightBottom):
        """ 设置变换后的边角坐标 """
        self.dstPoints = numpy.float32(
            [leftTop, rightTop, leftBottom, rightBottom])

    def getPerspectiveTransform(self, imWidth, imHeight, isGetQPixmap: bool = False) -> QPixmap:
        """ 透视变换图像，返回QPixmap """
        # 如果是jpg需要加上一个透明通道
        if self.src.shape[-1] == 3:
            self.src = cv.cvtColor(self.src, cv.COLOR_BGR2BGRA)
        # 透视变换矩阵
        perspectiveMatrix = cv.getPerspectiveTransform(
            self.srcPoints, self.dstPoints)
        # 执行变换
        self.dst = cv.warpPerspective(self.src, perspectiveMatrix, (
            imWidth, imHeight), borderMode=cv.BORDER_CONSTANT, borderValue=[0, 0, 0, 0])
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

if __name__=='__main__':

    trans = PerspectiveTransform('resource\\Album_Cover\\Assortrip\\Assortrip.jpg')
    trans.setDstPoints(
        [2, 0], [trans.width-3, 3], [1, trans.height-2], [trans.width-5, trans.height-3])
    trans.getPerspectiveTransform(trans.width, trans.height)
    trans.show()
    trans.save('test.png')
