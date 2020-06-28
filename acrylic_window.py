import sys
from ctypes import *

from ctypes.wintypes import HWND
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon,QPixmap,QBitmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QAction, QGraphicsDropShadowEffect,QPushButton,QGridLayout
from effects.window_effect import WindowEffect
from my_widget.my_menu import Menu

class Window(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 500)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.Window)
        self.hWnd= HWND(int(self.winId()))
        #实例化图片和按钮
        self.pic = QLabel(self)
        #实例化窗口特效
        self.winEffect = WindowEffect()
        self.winEffect.setAeroEffect(self.hWnd)
        self.circleMask = QBitmap(QPixmap('resource\\images\\mask.png').scaled(500, 500))
        self.setMask(self.circleMask)
        
        #实例化菜单和动作
        self.initWidget()
        
    def initWidget(self):
        """ 初始化小部件 """
        self.pic.move(130, 130)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet('background:rgba(255,0,0,200)')
        self.pic.setPixmap(QPixmap('resource\\Album Cover\\人間開花\\人間開花.jpg'))

    def contextMenuEvent(self, e):
        self.menu.exec(self.cursor().pos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setAttribute(Qt.AA_NativeWindows)
    demo = Window()
    demo.show()
    sys.exit(app.exec_())
