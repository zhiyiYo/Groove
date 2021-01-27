# coding:utf-8

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage

from my_functions.gaussian_blur import getBlurPixmap


class BlurCoverThread(QThread):
    """ 磨砂专辑封面线程 """
    blurDone = pyqtSignal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置磨砂标志位
        self.albumCoverPath = ''
        self.blurPixmap = None
        self.blurRadius = 7
        self.bluredPicMaxSize = (450, 450)

    def __blurAlbumCover(self):
        """ 得到磨砂后的pixmap """
        self.blurPixmap = getBlurPixmap(
            self.albumCoverPath, self.blurRadius, 0.8, self.bluredPicMaxSize)

    def run(self):
        """ 开始磨砂 """
        if self.albumCoverPath:
            self.__blurAlbumCover()
            self.blurDone.emit(self.blurPixmap)

    def setTargetCover(self, albumCoverPath, blurRadius=6, bluredPicMaxSize=(450, 450)):
        """ 设置磨砂的目标图片 """
        self.albumCoverPath = albumCoverPath
        self.blurRadius = blurRadius
        self.bluredPicMaxSize = bluredPicMaxSize
