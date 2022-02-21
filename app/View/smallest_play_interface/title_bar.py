# coding:utf-8
from win32.lib import win32con
from win32.win32api import SendMessage
from win32.win32gui import ReleaseCapture

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QWidget

from components.buttons.three_state_button import ThreeStateButton


class TitleBar(QWidget):
    """ Title bar """

    def __init__(self, parent):
        super().__init__(parent)
        self.closeButton = ThreeStateButton(
            {
                "normal": ":/images/title_bar/透明白色关闭按钮_57_40.png",
                "hover": ":/images/title_bar/关闭按钮_hover_57_40.png",
                "pressed": ":/images/title_bar/关闭按钮_pressed_57_40.png",
            },
            self,
            (57, 40)
        )
        self.resize(350, 40)
        self.setFixedHeight(40)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.closeButton.clicked.connect(self.window().close)

    def resizeEvent(self, e: QResizeEvent):
        self.closeButton.move(self.width() - self.closeButton.width(), 0)

    def mousePressEvent(self, event):
        if 0 < event.pos().x() < self.closeButton.x():
            ReleaseCapture()
            SendMessage(self.window().winId(), win32con.WM_SYSCOMMAND,
                        win32con.SC_MOVE + win32con.HTCAPTION, 0)
            event.ignore()
