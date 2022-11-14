# coding:utf-8
from components.widgets.menu import DWMMenu
from common.style_sheet import setStyleSheet
from common.window_effect import WindowEffect
from PyQt5.QtCore import QEasingCurve, QEvent, QPoint, QPropertyAnimation, QRect, Qt
from PyQt5.QtWidgets import QApplication, QMenu


class MoreActionsMenu(DWMMenu):
    """ More actions menu """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

        self.setObjectName("appBarMoreActionsMenu")
        setStyleSheet(self, 'menu')

    def exec(self, pos: QPoint):
        """ show menu """
        # prevent menus from exceeding the screen display area
        h = len(self.actions())*38 + 10
        w = max(self.fontMetrics().width(i.text()) for i in self.actions()) + 45
        desktop = QApplication.desktop().availableGeometry()
        pos.setX(min(pos.x(), desktop.width() - w))
        pos.setY(min(pos.y(), desktop.height() - h))

        self.animation.setStartValue(QRect(pos.x(), pos.y(), 1, h))
        self.animation.setEndValue(QRect(pos.x(), pos.y(), w, h))
        self.animation.start()
        super().exec(pos)
