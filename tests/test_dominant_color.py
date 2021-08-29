# coding:utf-8
import sys
import os
from math import floor
from colorthief import ColorThief

from common.image_process_utils import DominantColor

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QApplication


class DominantColor_:

    @classmethod
    def getDominantColor(cls, imagePath, resType=str):
        """ 获取主题色 """
        imagePath = imagePath
        colorThief = ColorThief(imagePath)

        # 调整图像大小，加快运算速度
        if max(colorThief.image.size) > 400:
            colorThief.image = colorThief.image.resize((400, 400))

        palette = colorThief.get_palette(quality=9)
        rgb = palette[0]
        if resType is str:
            rgb = "".join([hex(i)[2:].rjust(2, "0") for i in rgb])

        return rgb


class Demo(QWidget):
    """ 测试用例 """

    def __init__(self):
        super().__init__()
        self.dominantColor = DominantColor()
        self.setFixedSize(400, 400)
        self.currentAlbumIndex = 0
        self.albumFolder = "Album_Cover"
        self.getPicPaths()
        self.albumCoverLabel = QLabel(self)
        self.albumCoverLabel.setFixedSize(240, 240)
        self.nextPicBt = QPushButton("下一首", self)
        self.lastPicBt = QPushButton("上一首", self)
        # 初始化
        self.__initWidgets()

    def __initWidgets(self):
        """ 初始化小部件 """
        self.albumCoverLabel.move(80, 80)
        self.lastPicBt.move(100, 330)
        self.nextPicBt.move(self.width() - 100 - self.nextPicBt.width(), 330)
        # 信号连接到槽
        self.lastPicBt.clicked.connect(self.updateAlbumCover)
        self.nextPicBt.clicked.connect(self.updateAlbumCover)

    def getPicPaths(self):
        """ 扫描文件夹 """
        self.albumPath_list = []
        dirName_list = os.listdir(self.albumFolder)
        for folder in dirName_list:
            if os.path.isfile(folder):
                continue
            folder = os.path.join(self.albumFolder, folder)
            fileName_list = os.listdir(folder)
            for album in fileName_list:
                if album.endswith("png") or album.endswith("jpg"):
                    self.albumPath_list.append(os.path.join(folder, album))

    def updateAlbumCover(self):
        """ 更新专辑封面 """
        if self.sender() == self.lastPicBt:
            if self.currentAlbumIndex == 0:
                return
            self.currentAlbumIndex -= 1
        elif self.sender() == self.nextPicBt:
            if self.currentAlbumIndex == len(self.albumPath_list) - 1:
                return
            self.currentAlbumIndex += 1
        albumPath = self.albumPath_list[self.currentAlbumIndex]
        self.albumCoverLabel.setPixmap(
            QPixmap(albumPath).scaled(
                240, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        r, g, b = self.dominantColor.getDominantColor(albumPath, tuple)
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(r, g, b))
        self.setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
