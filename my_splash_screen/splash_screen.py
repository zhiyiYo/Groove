import sys
from ctypes.wintypes import HWND
from time import sleep

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPainter, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QSplashScreen, QGraphicsDropShadowEffect, QWidget



class SplashScreen(QSplashScreen):
    """ 子启动界面 """

    def __init__(self):
        super().__init__()
        self.icon = QPixmap('resource\\images\\icon.png')
        self.initWidget()
        # self.setShadowEffect()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(1360, 1030)
        self.setAttribute(Qt.WA_StyledBackground|Qt.WA_TranslucentBackground)
        # 居中显示
        desktop = QApplication.desktop()
        self.move(int(desktop.width() / 2 - self.width() / 2+2),
                  int((desktop.height()) / 2 - self.height() / 2-22))
        self.setShadowEffect()

    def resizeEvent(self, e):
        """ 窗口缩放时改变标题栏的长度 """
        super().resizeEvent(e)

    def paintEvent(self, e):
        """ 绘制背景 """
        #super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing|QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        brush = QBrush(QColor(0, 113, 217))
        painter.setBrush(brush)
        painter.drawRect(self.rect())
        painter.drawPixmap(int(self.width()/2-self.icon.width()/2), int(self.height(
        )/2-self.icon.height()/2), self.icon.width(), self.icon.height(), self.icon)

    def setShadowEffect(self):
        """ 添加阴影 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(30)
        self.shadowEffect.setOffset(0, 3)
        self.setGraphicsEffect(self.shadowEffect)


