import sys

import pinyin
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBitmap, QImage, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget,QPushButton)
    

class Demo(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(100,100)
        
        self.all_h_layout = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.gridLayout = QGridLayout()

        self.label_1 = QLabel('黄政之', self)
        self.label_2 = QLabel('付泽', self)
        self.label_3 = QLabel('许冰冰', self)
        self.bt_1 = QPushButton('移出网格', self)
        self.bt_1.clicked.connect(self.removeLayout)

        self.gridLayout.addWidget(self.label_1, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.bt_1,1,1,1,1)
        
        self.all_h_layout.addLayout(self.gridLayout)
        self.setLayout(self.all_h_layout)

    def removeLayout(self):
        del self.label_1
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())