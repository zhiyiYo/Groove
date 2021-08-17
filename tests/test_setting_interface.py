# coding:utf-8
import sys

from app.View.setting_interface import SettingInterface
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SettingInterface()
    w.show()
    sys.exit(app.exec_())
