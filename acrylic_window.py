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
        self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.CustomizeWindowHint)
        self.hWnd= HWND(int(self.winId()))
        #实例化图片和按钮
        self.pic = QLabel(self)
        self.bt = QPushButton('测试',self)
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
        self.bt.move(200,250)
        self.pic.move(130, 130)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setStyleSheet('background:white')
        self.winEffect.setShadowEffect(c_bool(False), self.hWnd, 0)
        #self.winEffect.setAcrylicEffect(self.hWnd, 0x16F2F2F2)
        # 设置按钮属性
        self.bt.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.bt.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground|Qt.WA_NoSystemBackground)
        self.bt.setStyleSheet('background:rgba(242,242,242,80)')
        self.winEffect.setAcrylicEffect(HWND(int(self.bt.winId())), 0x16F2F2F2)
        self.openAct.setProperty('subMenu',True)
        self.menu.addActions([self.openAct, self.saveAct])
        self.menu
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
