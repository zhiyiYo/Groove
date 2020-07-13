import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QRegion, QPainter, QPixmap, QBitmap, QColor, QBrush,QPen
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QGraphicsBlurEffect, QLabel


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(400, 400)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.widget=QWidget(self)
        self.widget.setStyleSheet('background:red')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
