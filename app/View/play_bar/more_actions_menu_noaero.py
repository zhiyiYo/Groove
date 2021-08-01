# coding:utf-8

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPainter, QPen
from PyQt5.QtWidgets import QAction, QGraphicsDropShadowEffect, QHBoxLayout, QMenu


class SubMoreActionsMenu(QMenu):
    """ 子更多操作圆角菜单，flag用来指示动作的类型，flag=0有四个动作，flag=1有三个动作 """

    def __init__(self, text="", parent=None, actionFlag=0):
        super().__init__(parent)
        self.actionFlag = actionFlag
        # 创建动作
        self.createActions()
        # 初始化界面
        self.initWidget()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setObjectName("roundBorderMenu")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint | Qt.Popup
        )
        self.setShadowEffect()

    def setShadowEffect(self):
        """ 添加阴影 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(30)
        self.shadowEffect.setOffset(0, 3)
        self.setGraphicsEffect(self.shadowEffect)

    def createActions(self):
        """ 创建动作"""
        self.savePlayListAct = QAction(
            QIcon("app/resource/images/menu/保存为播放列表.png"), "保存为播放列表", self
        )
        self.clearPlayListAct = QAction(
            QIcon("app/resource/images/menu/清空正在播放_16_16.png"), '清空"正在播放"', self
        )
        if self.actionFlag:
            self.showPlayListAct = QAction(
                QIcon("app/resource/images/menu/显示正在播放列表.png"), "显示正在播放列表", self
            )
            self.fillScreenAct = QAction(
                QIcon("app/resource/images/menu/转到全屏.png"), "转到全屏", self
            )
            self.action_list = [
                self.showPlayListAct,
                self.fillScreenAct,
                self.savePlayListAct,
                self.clearPlayListAct,
            ]
        else:
            self.showSongerCover = QAction("显示歌手封面", self)
            self.action_list = [
                self.savePlayListAct,
                self.showSongerCover,
                self.clearPlayListAct,
            ]
        # 将动作添加到菜单中
        self.clear()
        self.addActions(self.action_list)

    def paintEvent(self, e):
        """ 绘制圆角菜单 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(181, 181, 181))
        painter.setPen(pen)
        brush = QBrush(QColor(214, 214, 214))
        painter.setBrush(brush)
        painter.drawRoundedRect(self.rect(), 7, 7)
        super().paintEvent(e)

    def setQss(self):
        """ 设置层叠样式 """
        with open("app/resource/css/menu.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())


class MoreActionsMenu(QMenu):
    """ 更多操作圆角菜单，flag用来指示动作的类型，flag=1有四个动作，flag=0有三个动作 """

    def __init__(self, parent=None, actionFlag=1):
        super().__init__(parent)
        self.actionFlag = actionFlag
        # 创建动画
        self.animation = QPropertyAnimation(self, b"geometry")
        # 实例化子窗口
        self.subMenu = SubMoreActionsMenu(parent=self, actionFlag=self.actionFlag)
        # 实例化布局
        self.all_h_layout = QHBoxLayout(self)
        self.initWidget()
        self.initLayout()
        self.hide()

    def initWidget(self):
        """ 初始化小部件 """
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        # 初始化动画
        self.animation.setDirection(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        # 引用子菜单的动作
        self.savePlayListAct = self.subMenu.savePlayListAct
        self.clearPlayListAct = self.subMenu.clearPlayListAct
        if self.actionFlag:
            self.showPlayListAct = self.subMenu.showPlayListAct
            self.fillScreenAct = self.subMenu.fillScreenAct
        else:
            self.showSongerCover = self.subMenu.showSongerCover

    def initLayout(self):
        """ 初始化布局 """
        self.all_h_layout.addWidget(self.subMenu, 0, Qt.AlignCenter)
        self.all_h_layout.setContentsMargins(30, 30, 30, 30)

    def show(self, pos):
        """ 重载show() """
        self.move(pos)
        super().show()
