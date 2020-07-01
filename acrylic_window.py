import sys
from ctypes import *
from ctypes.wintypes import HWND

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QBitmap, QIcon, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect,
                             QGridLayout, QLabel, QPushButton, QWidget,QSlider)

from effects.window_effect import WindowEffect
from my_play_bar.more_actions_menu import MoreActionsMenu


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
        """ self.winEffect.setAcrylicEffect(self.hWnd)
        self.setStyleSheet('QWidget{background:transparent}') """
        self.button=QPushButton('测试',self)
        self.menu = MoreActionsMenu(parent=self, actionFlag=0)
        self.menu.hide()
        
        #实例化菜单和动作
        self.initWidget()
        
    def initWidget(self):
        """ 初始化小部件 """
        self.pic.move(130, 130)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        self.pic.setPixmap(QPixmap('resource\\Album Cover\\人間開花\\人間開花.jpg'))
        self.menu.savePlayListAct.triggered.connect(self.saveActEvent)

    def contextMenuEvent(self, e):
        self.menu.show(self.cursor().pos())

    def saveActEvent(self):
        print(1)
        self.menu.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Window()
    demo.show()
    sys.exit(app.exec_())
