import sys

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage

sys.path.append('..')
from Groove.my_functions.gaussian_blur import getBlurPixmap

class BlurCoverThread(QThread):
    """ 磨砂专辑封面线程 """
    blurDone = pyqtSignal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置磨砂标志位
        self.__albumCoverPath = ''
        self.blurPixmap = None

    def __blurAlbumCover(self):
        """ 得到磨砂后的pixmap """
        self.blurPixmap = getBlurPixmap(self.__albumCoverPath, 18, 0.8)

    def run(self):
        """ 开始磨砂 """
        self.__blurAlbumCover()
        self.blurDone.emit(self.blurPixmap)

    def setTargetCover(self,albumCoverPath):
        """ 设置磨砂的目标图片 """
        self.__albumCoverPath = albumCoverPath