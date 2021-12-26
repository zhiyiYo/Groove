# coding:utf-8

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGroupBox


class GroupBox(QGroupBox):
    """ 标题栏可点击的分组箱 """

    titleClicked = pyqtSignal(str)

    def __init__(self, title: str = '', parent=None):
        super().__init__(title, parent)

    def mousePressEvent(self, e):
        """ 鼠标点击发送信号 """
        if self.childAt(e.pos()) or e.y() > 30:
            return
        self.titleClicked.emit(self.title())