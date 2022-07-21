# coding:utf-8
import sys

from common.utils import startSystemMove

from components.title_bar import TitleBarButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QWidget


class TitleBar(QWidget):
    """ Title bar """

    def __new__(cls, *args, **kwargs):
        cls = WindowsTitleBar if sys.platform == "win32" else LinuxTitleBar
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, parent):
        super().__init__(parent)
        self.closeButton = TitleBarButton(parent=self)
        self.closeButton.setObjectName('closeButton')
        self.resize(350, 40)
        self.setFixedHeight(40)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.closeButton.clicked.connect(self.window().close)

    def resizeEvent(self, e: QResizeEvent):
        self.closeButton.move(self.width() - self.closeButton.width(), 0)

    def _isDragRegion(self, pos):
        return not self.closeButton.isPressed and 0 < pos.x() < self.closeButton.x()


class WindowsTitleBar(TitleBar):

    def mouseMoveEvent(self, event):
        if not self._isDragRegion(event.pos()):
            return

        startSystemMove(self.window(), event.globalPos())


class LinuxTitleBar(TitleBar):
    """ Title bar for Linux system """

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or not self._isDragRegion(event.pos()):
            return

        startSystemMove(self.window(), event.globalPos())