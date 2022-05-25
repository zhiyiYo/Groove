# coding:utf-8
import os
import sys

from PyQt5.QtCore import QLocale, Qt, QTranslator
from PyQt5.QtWidgets import QApplication

from common.os_utils import getDevicePixelRatio
from View.main_window import MainWindow


# fix problem: qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
if "QT_QPA_PLATFORM_PLUGIN_PATH" in os.environ:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")

# enable high dpi scale
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = str(max(1, getDevicePixelRatio()-0.25))
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
app.setStyle("Windows")

# Internationalization
translator = QTranslator()
translator.load(QLocale.system(), ":/i18n/Groove_")
app.installTranslator(translator)

# create main window
groove = MainWindow()
groove.show()

app.exec_()