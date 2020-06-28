import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt, QAbstractAnimation, QPropertyAnimation
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 100)
        self.bt1 = QPushButton(self)
        self.bt1.setFixedSize(150,100)
        self.bt1.setMinimumWidth(150)
        self.bt2 = QPushButton(self)
        self.bt3 = QPushButton(self)
        self.bt3.setFixedSize(200,100)
        self.bt2.move(150, 0)
        self.bt3.hide()
        self.bt1.clicked.connect(self.changeBtSize)
        self.bt3.clicked.connect(self.changeBtSize)
        self.currentBt = self.bt1
        print(self.window(),self)
    
    def changeBtSize(self):
        sender = self.sender()
        if sender.width() == 150:
            self.bt1.hide()
            self.bt3.show()
            self.currentBt=self.bt2
        else:
            self.bt3.hide()
            self.bt1.show()
            self.currentBt=self.bt1
        self.bt2.resize(self.width() - self.currentBt.width(), self.bt2.height())
        self.bt2.move(self.currentBt.width(),0)
        
    def resizeEvent(self, e):
        self.bt2.resize(self.width() - self.currentBt.width(), self.bt2.height())
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
