# coding:utf-8

""" 自定义按钮库"""

import sys

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QBitmap, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton


class SongerPlayButton(QPushButton):
    """ 歌手头像上的播放按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 隐藏边框
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置鼠标没有hover时的遮罩
        self.mask = QBitmap('resource\\images\\play_button_mask_57_57.svg')
        self.resize(self.mask.size())
        self.setMask(self.mask)

        # 设置监听
        self.installEventFilter(self)

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pix = QPixmap('resource\\images\\歌手播放按钮_67_67.png')
        painter.drawPixmap(0, 0, self.width(), self.height(), pix)

    def eventFilter(self, obj, e):
        """ hover时变大,没有hover时变小 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.mask = QBitmap(
                    'resource\\images\\play_button_mask_67_67.svg')
                self.resize(self.mask.size())
                self.setMask(self.mask)
            elif e.type() == QEvent.Leave:
                self.mask = QBitmap(
                    'resource\\images\\play_button_mask_57_57.svg')
                self.resize(self.mask.size())
                self.setMask(self.mask)

        return False


class SongerAddToButton(QPushButton):
    """ 歌手头像上的添加到按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 隐藏边框
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置遮罩
        self.mask = QBitmap('resource\\images\\play_button_mask_57_57.svg')
        self.resize(self.mask.size())
        self.setMask(self.mask)

        # 设置监听
        self.installEventFilter(self)

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pix = QPixmap('resource\\images\\歌手添加到按钮1.png')
        painter.drawPixmap(0, 0, self.width(), self.height(), pix)

    def eventFilter(self, obj, e):
        """ hover时变大,没有hover时变小 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.mask = QBitmap(
                    'resource\\images\\play_button_mask_67_67.svg')
                self.resize(self.mask.size())
                self.setMask(self.mask)
            elif e.type() == QEvent.Leave:
                self.mask = QBitmap(
                    'resource\\images\\play_button_mask_57_57.svg')
                self.resize(self.mask.size())
                self.setMask(self.mask)

        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongerPlayButton()
    demo.show()
    sys.exit(app.exec_())
