import sys

from PyQt5.QtCore import QEvent, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QEnterEvent, QMouseEvent, QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QLabel, QToolTip, QWidget

from my_functions.get_pressed_pos import getPressedPos
from my_functions.is_not_leave import isNotLeave


class ClickableLabel(QLabel):
    """ 定义可发出点击信号的Label """
    # 创建点击信号
    clicked = pyqtSignal()

    def __init__(self, text='', parent=None, isSendEventToParent: bool = True):
        super().__init__(text, parent)
        self.isSendEventToParent = isSendEventToParent

    def mousePressEvent(self, e):
        """ 处理鼠标点击 """
        if self.isSendEventToParent:
            super().mousePressEvent(e)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ 鼠标松开时发送信号 """
        if self.isSendEventToParent:
            super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

class ErrorIcon(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置提示条
        self.customToolTip = None
        self.setPixmap(
            QPixmap('resource\\images\\empty_lineEdit_error.png'))
        self.setFixedSize(21, 21)
