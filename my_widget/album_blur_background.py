import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGraphicsBlurEffect,QGraphicsDropShadowEffect


class AlbumBlurBackground(QWidget):
    """ 定义专辑的磨砂背景 """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 实例化背景和磨砂效果
        self.backgroundPic = QLabel(self)
        self.blurEffect = QGraphicsBlurEffect(self)
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(220,220)
        self.backgroundPic.resize(215, 215)
        self.shadowEffect.setBlurRadius(5)
        self.shadowEffect.setOffset(0)
        self.shadowEffect.setColor(QColor("#bbbbbb"))
        self.backgroundPic.setScaledContents(True)
        self.blurEffect.setBlurRadius(30)
        self.backgroundPic.setGraphicsEffect(self.blurEffect)
        self.setGraphicsEffect(self.shadowEffect)
