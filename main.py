import json
import re
import sys
from ctypes.wintypes import HWND
from PyQt5.QtCore import QRect, QSize, Qt, QEvent,QPoint
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap,QEnterEvent,QBitmap,QRegion
from PyQt5.QtWidgets import (QPushButton,
                             QApplication, QWidget, QLabel, QGraphicsBlurEffect, QGraphicsOpacityEffect)
from effects.window_effect import WindowEffect


class Father(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 500)
        self.move(500, 100)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.widget=QWidget(self)
        self.label = QLabel('测试', self.widget)
        self.label.move(100, 100)
        mask = QRegion(self.frameGeometry())
        mask -= QRegion(self.geometry())
        #mask+=QRegion(self.childrenRegion())
        self.setMask(mask)
        
    def enterEvent(self, e):
        print(f'窗口的全局坐标为：{self.mapToGlobal(self.label.pos())}')



if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Father()
    demo.show()
    sys.exit(app.exec_())
