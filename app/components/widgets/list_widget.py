# coding:utf-8
from common.smooth_scroll import SmoothScroll
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QWheelEvent, QCursor
from PyQt5.QtWidgets import QApplication, QListWidget


class ListWidget(QListWidget):
    """ A list widget which can scroll smoothly """

    def __init__(self, parent=None, trigger=False):
        super().__init__(parent)
        self.setDragEnabled(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setAttribute(Qt.WA_StyledBackground)
        self.smoothScroll = SmoothScroll(self)

        if trigger:
            self.verticalScrollBar().valueChanged.connect(self.__fakeMoveMouse)

    def __fakeMoveMouse(self):
        """ fake move mouse """
        QCursor.setPos(QCursor.pos() + QPoint(0, 1))
        QApplication.processEvents()
        QCursor.setPos(QCursor.pos() - QPoint(0, 1))

    def wheelEvent(self, e: QWheelEvent):
        self.smoothScroll.wheelEvent(e)
