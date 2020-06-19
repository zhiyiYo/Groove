import json
import re
import sys

from PyQt5.QtCore import QRect, QSize, Qt,QEvent
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QGraphicsBlurEffect, QGraphicsOpacityEffect)


class Demo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background:white')
        self.resize(220,303)
        self.pic = QLabel(self)
        self.album=QLabel(self)
        self.name=QLabel('测试专辑名',self)
        self.blurEffect = QGraphicsBlurEffect(self.pic)
        self.pic.setPixmap(QPixmap('resource\\Album Cover\\人間開花\\人間開花.jpg').scaled(215,215))
        self.album.setPixmap(QPixmap(
            'resource\\Album Cover\\人間開花\\人間開花.jpg').scaled(200, 200))
        self.blurEffect.setBlurRadius(35)
        self.pic.setGraphicsEffect(self.blurEffect)
        self.pic.move(0, 10)
        self.album.move(10,10)
        self.name.move(10, 220)
        self.name.setStyleSheet('background:transparent;font:16px "Microsoft YaHei"')


class Father(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background:white')
        self.op=QGraphicsOpacityEffect(self)
        self.resize(220,303)
        self.demo = Demo(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo=Father()
    demo.show()
    sys.exit(app.exec_())
