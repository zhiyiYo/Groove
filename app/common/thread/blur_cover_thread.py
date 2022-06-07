# coding:utf-8
from common.image_utils import DominantColor, getBlurPixmap
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap


class BlurCoverThread(QThread):
    """ Blur album cover thread """

    blurFinished = pyqtSignal(QPixmap, QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.coverPath = ""
        self.blurPixmap = None
        self.blurRadius = 7
        self.maxSize = (450, 450)

    def run(self):
        """ start to blur """
        if not self.coverPath:
            return

        color = DominantColor.getDominantColor(self.coverPath)
        self.blurPixmap = getBlurPixmap(
            self.coverPath, self.blurRadius, 0.85, self.maxSize)
        self.blurFinished.emit(self.blurPixmap, QColor(*color))

    def setCover(self, coverPath: str, blurRadius=6, maxSize: tuple = (450, 450)):
        """ set the album cover to blur

        Parameters
        ----------
        coverPath: str
            album cover path

        blurRadius: int
            blur radius

        maxSize: tuple
            the maximum size of image, if the actual picture exceeds this size,
            it will be scaled to speed up the computation speed.
        """
        self.coverPath = coverPath
        self.blurRadius = blurRadius
        self.maxSize = maxSize
