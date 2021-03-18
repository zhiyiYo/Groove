# coding:utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget


class SubPanelFrame(QDialog):
    """ 子面板的外围框架 """
    def __init__(self, parent=None,isWindow=True):
        self.isWindow = isWindow
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        if self.isWindow:
            self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint)
    
    def showMask(self):
        """ 显示Mask """
        if self.parent():
            parent_rect = self.parent().geometry()
            if not self.isWindow:
                self.setGeometry(0, 0,
                                parent_rect.width(), parent_rect.height())
            else:
                self.setGeometry(parent_rect)
            self.createWindowMask()

    def createWindowMask(self):
        """ 创建白色透明遮罩 """
        self.windowMask = QWidget(self)
        self.windowMask.setStyleSheet('background:rgba(255,255,255,177)')
        self.windowMask.resize(self.size())
        self.windowMask.lower()
