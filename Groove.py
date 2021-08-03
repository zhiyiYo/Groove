# coding:utf-8
import sys
from time import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from app.View.main_window import MainWindow

app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
font = QFont("Microsoft YaHei", 11)
font.setStyleStrategy(QFont.PreferAntialias)
app.setFont(font)
t1 = time()
groove = MainWindow()
t2 = time()
print("创建所有界面耗时：".ljust(19), t2 - t1)
groove.show()
sys.exit(app.exec_())