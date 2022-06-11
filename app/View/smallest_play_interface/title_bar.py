# coding:utf-8
import sys

if sys.platform == "win32":
    from win32.lib import win32con
    from win32.win32api import SendMessage
    from win32.win32gui import ReleaseCapture
else:
    from common.linux_utils import LinuxMoveResize

from components.title_bar import TitleBarButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QWidget


class TitleBar(QWidget):
    """ Title bar """

    def __new__(cls, *args, **kwargs):
        cls = WindowsTitleBar if sys.platform == "win32" else UnixTitleBar
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
        return 0 < pos.x() < self.closeButton.x()


class WindowsTitleBar(TitleBar):

    def mouseMoveEvent(self, event):
        if not self._isDragRegion(event.pos()):
            return

        ReleaseCapture()
        SendMessage(self.window().winId(), win32con.WM_SYSCOMMAND,
                    win32con.SC_MOVE + win32con.HTCAPTION, 0)
        event.ignore()


class UnixTitleBar(TitleBar):
    """ Title bar for Unix system """

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or not self._isDragRegion(event.pos()):
            return

        pos = event.globalPos()
        LinuxMoveResize.startSystemMove(self.window(), pos)
