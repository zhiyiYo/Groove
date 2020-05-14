import sys
import time
from PyQt5.QtCore import QPoint, Qt, QSize, QEvent
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,QScrollBar,QLabel,
                             QLayout, QMenu, QPushButton, QVBoxLayout, QWidget)


class Demo(QWidget):

    def __init__(self):
        super().__init__()

        self.resize(200,100)
        self.scrollBar = QScrollBar(self)
        self.label = QLabel('测试', self)
        self.label2=QLabel('测试2',self)
        self.h_layout = QHBoxLayout()
        
        self.h_layout.addWidget(self.label, 0, Qt.AlignLeft)
        self.h_layout.addWidget(self.label2, 0, Qt.AlignRight)
        self.scrollBar.move(self.width()-self.scrollBar.width(),0)

        self.setLayout(self.h_layout)

    def resizeEvent(self, e):
        self.scrollBar.move(self.width()-self.scrollBar.width(), 0)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)

    mySongTab = Demo()
    mySongTab.show()

    sys.exit(app.exec_())
