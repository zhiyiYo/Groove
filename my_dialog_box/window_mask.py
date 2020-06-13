import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QApplication, QWidget


class WindowMask(QWidget):
    """ 定义一个白色的半透明遮罩 """

    def __init__(self,  parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyleSheet('background:rgba(255,255,255,172);')

    def show(self):
        """ 获取父窗口的位置后显示 """
        if self.parent() is None:
            return
        parent_rect = self.parent().geometry()

        self.setGeometry(0, 0, parent_rect.width(), parent_rect.height())
        super().show()
