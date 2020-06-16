import sys
from ctypes import c_bool, cdll
from ctypes.wintypes import HWND

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect,
                             QMenu, QWidget)
sys.path.append('..')
from Groove.effects.setEffect import setAcrylicEffect, setShadowEffect




class Menu(QMenu):
    """ 自定义菜单 """

    def __init__(self, string=None, parent=None):
        super().__init__(string,parent)
        self.class_amanded = c_bool(False)
        self.setQss()
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.hWnd = HWND(int(self.winId()))
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ 开启特效 """
        dll = cdll.LoadLibrary('acrylic_dll\\acrylic.dll')
        # 添加阴影
        self.class_amended = setShadowEffect(
            dll, self.class_amended, self.hWnd)
        # 设置磨砂效果
        #setAcrylicEffect(dll,self.hWnd,0x16FF52F2)
        #cdll.LoadLibrary('acrylic_dll\\aero.dll').setBlur(self.hWnd)

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\menu.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
