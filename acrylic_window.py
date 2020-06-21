import sys
from ctypes import *

from ctypes.wintypes import HWND
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QAction, QGraphicsDropShadowEffect,QPushButton,QGridLayout
from effects.window_effect import WindowEffect
from my_widget.my_menu import Menu

class Window(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 500)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.hWnd= HWND(int(self.winId()))
        #实例化图片和按钮
        self.pic = QLabel(self)
        #实例化窗口特效
        self.winEffect=WindowEffect()
        
        #实例化菜单和动作
        self.menu = Menu(parent=self)
        self.subMenu=Menu('添加到',parent=self)
        self.openAct = QAction('打开', self)
        self.saveAct = QAction('保存', self)
        self.initWidget()
        
        
    def initWidget(self):
        """ 初始化小部件 """
        self.pic.move(130, 130)
        self.winEffect.setWindowFrame(self.hWnd,0,0,0,0)
        self.openAct.setProperty('subMenu',True)
        self.menu.addActions([self.openAct, self.saveAct])
        self.menu.addMenu(self.subMenu)
        self.pic.setPixmap(QPixmap('resource\\Album Cover\\人間開花\\人間開花.jpg'))


    def contextMenuEvent(self, e):
        self.menu.exec(self.cursor().pos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setAttribute(Qt.AA_NativeWindows)
    demo = Window()
    demo.show()
    sys.exit(app.exec_())
