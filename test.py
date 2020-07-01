import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import QRect, QSize, Qt,QEvent
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QGraphicsBlurEffect, QGraphicsOpacityEffect)
from effects.window_effect import WindowEffect


class Demo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(220, 303)
        self.hWnd = HWND(int(self.winId()))
        self.windowEffect = WindowEffect()
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.windowEffect.setAcrylicEffect(self.hWnd)
        self.windowEffect.setWindowFrame(self.hWnd,0,0,0,0)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
