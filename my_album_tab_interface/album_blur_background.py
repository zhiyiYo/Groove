import sys

from PIL import Image
from PIL.ImageFilter import GaussianBlur
from PIL.ImageQt import ImageQt

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication,  QLabel, QWidget, QGraphicsOpacityEffect


class AlbumBlurBackground(QWidget):
    """ 专辑卡磨砂背景 """

    def __init__(self, parent=None, imagePath: str = '', imageSize: tuple = (210, 210), blurRadius=30):
        """ 创建专辑卡磨砂背景窗口
        Parameters
        ----------
        imagePath : 专辑封面路径\n
        imageSize : 调整大小后的图片尺寸\n
        blurRadius : 磨砂半径, 磨砂后的图片尺寸将等于磨砂半径*2加上宽和高 """
        super().__init__(parent)
        self.__blurImage = None
        self.setBlurAlbum(imagePath, imageSize, blurRadius)

    def setBlurAlbum(self, imagePath: str, imageSize: tuple = (210, 210), blurRadius=30):
        """ 更新磨砂专辑封面 """
        self.__imagePath = imagePath
        self.__imageSize = imageSize
        self.__blurRadius = blurRadius
        if not imagePath:
            return
        # 读入专辑封面
        albumCover = Image.open(imagePath).resize(
            imageSize)  # type:Image.Image
        # 创建一个新图像
        blurAlbumCover = Image.new(
            'RGBA', (imageSize[0]+2*blurRadius, imageSize[1]+2*blurRadius), (255, 255, 255, 0))
        blurAlbumCover.paste(albumCover, (blurRadius, blurRadius))
        # 对图像进行高斯模糊
        blurAlbumCover = blurAlbumCover.filter(GaussianBlur(blurRadius/2))
        self.__blurImage = ImageQt(blurAlbumCover)
        # 调整窗口大小
        self.resize(*blurAlbumCover.size)
        # 绘制磨砂图
        self.update()

    def setBlurRadius(self, blurRadius):
        """ 设置磨砂半径 """
        self.__blurRadius = blurRadius

    def paintEvent(self, e):
        """ 绘制磨砂图 """
        super().paintEvent(e)
        if not self.__blurImage:
            return
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        painter.drawImage(0, 0, self.__blurImage)

    @property
    def blurRadius(self):
        return self.__blurRadius


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = AlbumBlurBackground(
        imagePath='resource\\Album_Cover\\人間開花\\人間開花.jpg')
    demo.show()
    sys.exit(app.exec_())
