import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from my_main_window import MainWindow



app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
font = QFont(QApplication.font())
font.setStyleStrategy(QFont.PreferAntialias)
app.setFont(font)
demo = MainWindow()
demo.show()
demo.playBar.show()
sys.exit(app.exec_())