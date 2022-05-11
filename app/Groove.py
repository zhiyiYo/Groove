# coding:utf-8
import os
import sys

from PyQt5.QtCore import QLocale, Qt, QTranslator
from PyQt5.QtWidgets import QApplication

from common.os_utils import getDevicePixelRatio
from View.main_window import MainWindow

# enable high dpi scale
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = str(max(1, getDevicePixelRatio()-0.25))
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# Internationalization
translator = QTranslator()
translator.load(QLocale.system(), ":/i18n/Groove_")
app.installTranslator(translator)

# create main window
groove = MainWindow()
groove.show()

app.exec_()