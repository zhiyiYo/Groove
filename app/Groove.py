# coding:utf-8
import os
import sys
from inspect import getsourcefile
from pathlib import Path

os.chdir(Path(getsourcefile(lambda: 0)).resolve().parent)


from PyQt5.QtCore import QLocale, Qt, QTranslator
from PyQt5.QtWidgets import QApplication

from common.application import SingletonApplication
from common.config import config
from common.dpi_manager import dpi_manager
from View.main_window import MainWindow


# fix bug: qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
if "QT_QPA_PLATFORM_PLUGIN_PATH" in os.environ:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")

# enable high dpi scale
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
if config.get(config.dpiScale) == "Auto":
    os.environ["QT_SCALE_FACTOR"] = str(max(1, dpi_manager.scale-0.25))
else:
    os.environ["QT_SCALE_FACTOR"] = str(config.get(config.dpiScale))

QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

app = SingletonApplication(sys.argv, "PyQt-Groove-Music")
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# Internationalization
translator = QTranslator()
translator.load(QLocale.system(), ":/i18n/Groove_")
app.installTranslator(translator)

# create main window
groove = MainWindow()
groove.show()

app.exec_()