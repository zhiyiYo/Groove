import numpy
from os import path

from PIL import Image
from PIL.ImageFilter import SMOOTH
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QPixmap


class PerspectiveTransform:

    def __init__(self):
        self.coeff = None
        self.image = None

    def setImage(self, img, size: tuple = None):
        """ 设置透视变换的图像，img可以是图片路径，也可以是QPixmap """
        if isinstance(img, str):
            if not path.exists(img):
                raise FileNotFoundError('图片不存在')
            self.image = Image.open(img)  # type:Image.Image
        elif isinstance(img, QPixmap):
            self.image = Image.fromqpixmap(img)
        else:
            raise Exception('img必须是图片路径字符串或者QPixmap对象')
        # 调整图像大小
        if size:
            self.imageSize = size
            self.image = self.image.resize(size)

    def findCoeffs(self, pa: list, pb: list):
        """ 计算透视变换系数
        Parameters
        ----------
        pa : 原图像的四个边角坐标，顺序为左上->右上->右下->左下\n
        pb : 变换后的图像的四个边角坐标 """
        matrix = []
        for p1, p2 in zip(pb, pa):
            matrix.append([p1[0], p1[1], 1, 0, 0, 0, -
                           p2[0]*p1[0], -p2[0]*p1[1]])
            matrix.append([0, 0, 0, p1[0], p1[1], 1, -
                           p2[1]*p1[0], -p2[1]*p1[1]])
        A = numpy.matrix(matrix, dtype=numpy.float)
        B = numpy.array(pa).reshape(8)
        res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
        self.coeffs = numpy.array(res).reshape(8)

    def getPerspectiveTransform(self, imgSize: tuple = None, fillColor='#FFFFFF00'):
        """ 根据得到的透视变换系数对图像进行变换
        Parameters
        ----------
        imgSize : 透视变换后的图像大小\n
        fillcolor : 空白部分的填充颜色 """
        if not imgSize:
            imgSize = self.image.size
        img = self.image.transform(imgSize, Image.PERSPECTIVE, self.coeffs,
                                   Image.BICUBIC, fillcolor=fillColor)
        img.save('per.png')


if __name__ == "__main__":
    trans = PerspectiveTransform()
    trans.setImage('resource\\Album_Cover\\Answer\\Answer.jpg')
    trans.findCoeffs([(0, 0), (239, 0), (239, 239), (0, 239)], [
                     (6, 4), (237, 1), (239, 239), (0, 239)])
    trans.getPerspectiveTransform()
