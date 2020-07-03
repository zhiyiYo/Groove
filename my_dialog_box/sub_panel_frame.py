import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog,QWidget


class SubPanelFrame(QDialog):
    """ 子面板的外围框架 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
    
    def showMask(self):
        """ 显示Mask """
        if self.parent():
            parent_rect = self.parent().geometry()
            self.setGeometry(parent_rect.x(), parent_rect.y(),
                             parent_rect.width(), parent_rect.height())
            self.createWindowMask()

    def createWindowMask(self):
        """ 创建白色透明遮罩 """
        self.windowMask = QWidget(self)
        self.windowMask.setStyleSheet('background:rgba(255,255,255,177)')
        self.windowMask.resize(self.size())
        self.windowMask.lower()
