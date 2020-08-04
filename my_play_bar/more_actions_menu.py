import sys

from PyQt5.QtCore import QEasingCurve, QEvent, QPropertyAnimation, QRect, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

from my_widget.my_menu import Menu


class MoreActionsMenu(Menu):
    """ 更多操作圆角菜单，actionFlag用来指示动作的类型，actionFlag=1有四个动作，actionFlag=0有三个动作 """

    def __init__(self, parent=None, actionFlag=1):
        super().__init__(parent=parent)
        self.actionFlag = actionFlag
        # 创建动作和动画
        self.createActions()
        self.animation = QPropertyAnimation(self, b'geometry')
        # 初始化界面
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.setObjectName('moreActionsMenu')
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

    def createActions(self):
        """ 创建动作"""
        self.savePlayListAct = QAction(
            QIcon('resource\\images\\menu\\保存为播放列表.png'), '保存为播放列表', self)
        self.clearPlayListAct = QAction(
            QIcon('resource\\images\\menu\\清空正在播放_16_16.png'), '清空"正在播放"',
            self)
        if self.actionFlag:
            self.showPlayListAct = QAction(
                QIcon('resource\\images\\menu\\显示正在播放列表.png'), '显示正在播放列表',
                self)
            self.fillScreenAct = QAction(
                QIcon('resource\\images\\menu\\转到全屏.png'), '转到全屏', self)
            self.action_list = [
                self.showPlayListAct, self.fillScreenAct, self.savePlayListAct,
                self.clearPlayListAct]
            self.actionNum = 4
        else:
            self.showSongerCover = QAction('显示歌手封面', self)
            self.action_list = [
                self.savePlayListAct, self.showSongerCover, self.clearPlayListAct]
            self.actionNum = 3
        self.addActions(self.action_list)

    def exec(self, pos):
        """ 重写exec_() """
        height = self.actionNum * 38
        self.animation.setStartValue(
            QRect(pos.x(), pos.y(), 1, height))
        self.animation.setEndValue(
            QRect(pos.x(), pos.y(), 206, height))
        # 开始动画
        self.animation.start()
        super().exec(pos)
