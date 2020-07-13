import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from my_splash_screen import SplashScreen


app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
font = QFont(QApplication.font())
font.setStyleStrategy(QFont.PreferAntialias)
app.setFont(font)
""" splashScreen = SplashScreen()
splashScreen.show()
app.processEvents()"""
demo = MainWindow()
demo.show()
demo.playBar.show()
#splashScreen.finish(demo)
sys.exit(app.exec_())
