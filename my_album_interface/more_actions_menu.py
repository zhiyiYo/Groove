# coding:utf-8

import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QEvent
from PyQt5.QtWidgets import QAction, QApplication, QMenu

from effects import WindowEffect


class MoreActionsMenu(QMenu):
    """ 更多操作菜单 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.windowEffect = WindowEffect()
        # 添加动画
        self.animation = QPropertyAnimation(self, b'geometry')
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setObjectName('albumInterfaceMoreActionMenu')
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        # 设置层叠样式
        self.__setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.hWnd = HWND(int(self.winId()))
            self.windowEffect.addShadowEffect(self.hWnd)
        return QMenu.event(self, e)

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\menu.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def setActionNum(self, actionNum):
        """ 设置动作的个数 """
        self.clear()
        self.actionNum = actionNum
        self.action_list = []
        self.deleteAct = QAction('删除', self)
        self.action_list.append(self.deleteAct)
        if actionNum >= 2:
            self.editInfoAct = QAction('编辑信息', self)
            self.action_list.append(self.editInfoAct)
            if actionNum == 3:
                self.pinToStartMenuAct = QAction('固定到"开始"菜单', self)
                self.action_list.append(self.pinToStartMenuAct)
        self.addActions(self.action_list[::-1])
        self.currentWidth = [120, 120, 168][self.actionNum - 1]
        self.currentHeight = self.actionNum * 38 + 10

    def exec(self, pos):
        """ 显示菜单 """
        self.animation.setStartValue(
            QRect(pos.x(), pos.y(), 1, self.currentHeight))
        self.animation.setEndValue(
            QRect(pos.x(), pos.y(), self.currentWidth, self.currentHeight))
        # 开始动画
        self.animation.start()
        super().exec(pos)
