import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QBitmap,QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from my_button import SongerAddToButton, SongerPlayButton

class AlbumCover(QWidget):
    """ 定义专辑封面 """

    def __init__(self,album_path):
        super().__init__()

        self.resize(200,200)

        # 实例化按钮
        self.playButton = SongerPlayButton(self)
        self.addToButton = SongerAddToButton(self)
        
        # 获取封面数据
        self.album_pic = QPixmap(album_path).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 初始化小部件
        self.initLayout()

    def initLayout(self):
        self.playButton.move(int(0.5 * self.width() - 36 - 0.5 * self.playButton.width()),
                             int(0.5*self.height() - 0.5*self.playButton.height()+1))

        self.addToButton.move(int(0.5*self.width()+36-0.5*self.playButton.width()),
                              int(0.5*self.height() - 0.5*self.playButton.height()+1))



