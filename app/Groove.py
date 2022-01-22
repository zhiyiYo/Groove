# coding:utf-8
import sys

from PyQt5.QtCore import QLocale, Qt, QTranslator
from PyQt5.QtWidgets import QApplication

from View.main_window import MainWindow
from common.database import DbInitializer


app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# 初始化数据库
DbInitializer()

# 国际化
translator = QTranslator()
translator.load(QLocale.system(), ":/i18n/Groove_")
app.installTranslator(translator)

# 创建主界面
groove = MainWindow()
groove.show()

app.exec_()