# coding:utf-8
from common.image_utils import getBlurPixmap
from common.picture import Avatar, AvatarType
from common.translator import Translator
from components.app_bar import AppBarButtonFactory as BF
from components.app_bar import CollapsingAppBarBase
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QColor, QPalette, QPixmap
from PyQt5.QtWidgets import QLabel


class SingerInfoBar(CollapsingAppBarBase):
    """ Singer information bar """

    def __init__(self, singerInfo: dict, parent=None):
        self.__getInfo(singerInfo)
        super().__init__(self.singer, self.genre, self.coverPath, 'singer', parent)

        self.setButtons([BF.PLAY, BF.ADD_TO, BF.ONLINE, BF.PIN_TO_START])

        self.blurLabel = BlurLabel(self.coverPath, 8, self)
        self.blurLabel.lower()
        self.blurLabel.setHidden(self.coverPath == AvatarType.BIG.value)

        self.setAutoFillBackground(True)

    def __getInfo(self, singerInfo: dict):
        """ get singer information """
        translator = Translator()
        self.singer = singerInfo.get('singer', translator.unknownArtist)
        self.genre = singerInfo.get('genre', translator.unknownGenre)
        self.albumInfos = singerInfo.get('albumInfos', [])
        self.coverPath = Avatar(self.singer).path(AvatarType.BIG)

    def setBackgroundColor(self):
        """ set the background color of bar """
        if self.coverPath == AvatarType.BIG.value:
            palette = QPalette()
            palette.setColor(self.backgroundRole(), QColor(24, 24, 24))
            self.setPalette(palette)

        if hasattr(self, 'blurLabel'):
            self.blurLabel.setHidden(self.coverPath == AvatarType.BIG.value)

    def updateWindow(self, singerInfo: dict):
        self.__getInfo(singerInfo)
        self.updateCover(self.coverPath)
        super().updateWindow(self.singer, self.genre, self.coverPath)

    def updateCover(self, coverPath: str):
        """ update cover """
        self.coverLabel.setPixmap(QPixmap(coverPath))
        self.blurLabel.updateWindow(coverPath, 8)
        self.__adjustBlurLabel()
        self.blurLabel.show()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.__adjustBlurLabel()

    def __adjustBlurLabel(self):
        """ adjust the size of cover """
        w = max(self.width(), self.height())
        self.blurLabel.resize(self.width(), self.height())
        self.blurLabel.setPixmap(self.blurLabel.pixmap().scaled(
            w, w, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))


class BlurLabel(QLabel):
    """ Blur label """

    def __init__(self, imagePath: str, blurRadius=30, parent=None):
        super().__init__(parent=parent)
        self.imagePath = imagePath
        self.blurRadius = blurRadius
        self.setPixmap(getBlurPixmap(imagePath, blurRadius, 0.85))

    def updateWindow(self, imagePath: str, blurRadius=30):
        """ update label """
        self.imagePath = imagePath
        self.blurRadius = blurRadius
        self.setPixmap(getBlurPixmap(imagePath, blurRadius, 0.85, (450, 450)))
