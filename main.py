import json
import re
import sys

from PyQt5.QtCore import QRect, QSize, Qt, QEvent
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QGraphicsBlurEffect, QGraphicsOpacityEffect)


class Father(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background:white')
        self.resize(200, 200)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Father()
    demo.show()
    sys.exit(app.exec_())
