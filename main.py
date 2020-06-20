import json
import re
import sys
from ctypes.wintypes import HWND
from PyQt5.QtCore import QRect, QSize, Qt, QEvent
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (QPushButton,
    QApplication, QWidget, QLabel, QGraphicsBlurEffect, QGraphicsOpacityEffect)
from effects.window_effect import WindowEffect

class Father(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 500)
        self.pic = QLabel(self)
        self.bt = QPushButton('测试', self)
        self.windowEffect = WindowEffect()
        
        self.initWidget()

    def initWidget(self):
        self.bt.move(200, 200)
        self.pic.move(130,130)
        self.bt.setStyleSheet('background:rgba(242,242,242,0.5)')
        self.bt.resize(100,100)
        self.bt.setAttribute(Qt.WA_TranslucentBackground|Qt.WA_StyledBackground)
        self.pic.setPixmap(QPixmap('resource\\Album Cover\\Red\\Red.jpg'))
        self.windowEffect.setAeroEffect(HWND(int(self.bt.winId())))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Father()
    demo.show()
    sys.exit(app.exec_())
