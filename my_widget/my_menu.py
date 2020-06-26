import sys
from ctypes import c_bool, cdll
from ctypes.wintypes import HWND

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIcon,QPainter,QPen,QColor,QIcon
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
        #self.windowEffect.setAcrylicEffect(self.hWnd, 0x10F2F2F2,1)
        self.windowEffect.setAeroEffect(self.hWnd)
        self.class_amended = c_bool(
            self.windowEffect.setShadowEffect(self.class_amended, self.hWnd))

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\menu.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class AddToMenu(Menu):
    """ 添加到菜单 """
    def __init__(self, string='添加到', parent=None):
        super().__init__(string, parent)
        # 创建动作
        self.createActions()

    def createActions(self):
        """ 创建三个动作 """
        self.playingAct = QAction(
            QIcon('resource\\images\\menu\\正在播放.png'), '正在播放', self)
        self.newPlayList = QAction(
            QIcon('resource\\images\\menu\\黑色加号.png'), '新的播放列表', self)
        self.myLove = QAction(
            QIcon('resource\\images\\menu\\黑色我喜欢_20_20.png'), '我喜欢', self)
        self.action_list = [self.playingAct, self.newPlayList, self.myLove]
        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlayList, self.myLove])
        
    def connectToSlots(self, slot_list: list):
        """ 将触发信号连接到槽函数 """
        for i in range(3):
            self.action_list[i].triggered.connect(slot_list[i])
            
