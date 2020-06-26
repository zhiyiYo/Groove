import json
import re
import sys
from ctypes.wintypes import HWND
from PyQt5.QtCore import QRect, QSize, Qt, QEvent,QPoint
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap,QEnterEvent,QBitmap,QRegion
from PyQt5.QtWidgets import (QPushButton,
                             QApplication, QWidget, QLabel, QGraphicsBlurEffect, QGraphicsOpacityEffect)
from effects.window_effect import WindowEffect
from my_widget.my_toolTip import ToolTip


class Father(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 500)
        self.move(500, 100)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.customToolTip = ToolTip('劇場版「ずっと前から好きでした。～告白実行委員会～」オリジナルサウンドトラック',self)
        self.label = MyLabel('测试',self.customToolTip, self)
        self.label.move(350, 250)
        #self.installEventFilter(self)
        
class MyLabel(QLabel):
    def __init__(self, text,tp=None, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet('font:20px "Microsoft YaHei"')
        self.tp=tp

    def enterEvent(self,e:QEnterEvent):
        if self.tp and not self.tp.isVisible():
            self.tp.move(e.globalX() -50, e.globalY() +80)
            self.tp.show()

    def leaveEvent(self, e):
        #print('鼠标离开标签事件触发，',end='')
        if self.tp and not self.tp.hasEnter:
            self.tp.hide()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Father()
    demo.show()
    sys.exit(app.exec_())
