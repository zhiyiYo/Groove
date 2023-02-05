# coding:utf-8
from common.smooth_scroll import SmoothScroll
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QListWidget


class ListWidget(QListWidget):
    """ A list widget which can scroll smoothly """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setAttribute(Qt.WA_StyledBackground)
        self.smoothScroll = SmoothScroll(self)

    def wheelEvent(self, e: QWheelEvent):
        self.smoothScroll.wheelEvent(e)
