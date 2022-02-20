# coding:utf-8
from typing import List

from common.window_effect import WindowEffect
from PyQt5.QtCore import (QEasingCurve, QEvent, QFile, QPoint,
                          QPropertyAnimation, QRect, Qt)
from PyQt5.QtWidgets import QAction, QMenu


class MoreActionsMenu(QMenu):
    """ More actions menu """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.action_list = []  # type:List[QAction]
        self.animation = QPropertyAnimation(self, b"geometry")
        self.windowEffect = WindowEffect()
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setObjectName("appBarMoreActionsMenu")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.__setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.windowEffect.addMenuShadowEffect(self.winId())
        return QMenu.event(self, e)

    def __setQss(self):
        """ set style sheet """
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def addActions(self, actions):
        super().addActions(actions)
        self.action_list.extend(actions)

    def addAction(self, action):
        super().addAction(action)
        self.action_list.append(action)

    def exec(self, pos: QPoint):
        """ show menu """
        w = max(self.fontMetrics().width(i.text())
                for i in self.action_list)+40
        h = len(self.action_list)*38+10
        self.animation.setStartValue(QRect(pos.x(), pos.y(), 1, h))
        self.animation.setEndValue(QRect(pos.x(), pos.y(), w, h))
        # 开始动画
        self.animation.start()
        super().exec(pos)
