import sys
from time import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from my_main_window import MainWindow

    
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
font = QFont('Microsoft YaHei')
font.setStyleStrategy(QFont.PreferAntialias)
app.setFont(font)
t1 = time()
demo = MainWindow()
t2 = time()
print('创建所有界面耗时：'.ljust(19), t2 - t1)
demo.show()
demo.playBar.show()
sys.exit(app.exec_())