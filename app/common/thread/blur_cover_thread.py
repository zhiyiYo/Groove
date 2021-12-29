# coding:utf-8

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

from common.image_process_utils import getBlurPixmap


class BlurCoverThread(QThread):
    """ 磨砂专辑封面线程 """

    blurFinished = pyqtSignal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.coverPath = ""
        self.blurPixmap = None
        self.blurRadius = 7
        self.maxSize = (450, 450)

    def run(self):
        """ 开始磨砂 """
        if self.coverPath:
            self.blurPixmap = getBlurPixmap(
                self.coverPath, self.blurRadius, 0.85, self.maxSize)
            self.blurFinished.emit(self.blurPixmap)

    def setCover(self, coverPath: str, blurRadius=6, maxSize: tuple = (450, 450)):
        """ 设置磨砂的目标图片

        Parameters
        ----------
        coverPath: str
            专辑封面路径

        blurRadius: int
            磨砂半径

        maxSize: tuple
            图片的最大尺寸，如果实际图片超过这个尺寸将被缩放以加快运算速度
        """
        self.coverPath = coverPath
        self.blurRadius = blurRadius
        self.maxSize = maxSize
