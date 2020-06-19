import sys
from ctypes import c_bool, cdll
from ctypes.wintypes import HWND

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIcon,QPainter,QPen,QColor
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect,
                             QMenu, QWidget)
sys.path.append('..')
from Groove.effects.window_effect import WindowEffect




class Menu(QMenu):
    """ 自定义菜单 """
    windowEffect = WindowEffect()

    def __init__(self, string=None, parent=None):
        super().__init__(string,parent)
        self.class_amended = c_bool(False)  
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup|Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground|Qt.WA_StyledBackground)
        self.setAutoFillBackground(False)
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.hWnd = HWND(int(self.winId()))
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ 开启特效 """
        # 设置阴影效果
        pass
        #self.windowEffect.addShadowEffect(1,self.hWnd)
        #self.windowEffect.setAcrylicEffect(self.hWnd, 0x10F2F2F2,1)
        self.windowEffect.setAeroEffect(self.hWnd)
        self.class_amended = c_bool(
            self.windowEffect.setShadowEffect(self.class_amended, self.hWnd))

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\menu.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
