import sys

from PyQt5.QtCore import QEvent, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QEnterEvent, QMouseEvent, QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QLabel, QToolTip, QWidget

from my_functions.get_pressed_pos import getPressedPos
from my_functions.is_not_leave import isNotLeave
from my_widget.my_toolTip import ToolTip


class ClickableLabel(QLabel):
    """ 定义可发出点击信号的Label """
    # 创建点击信号
    clicked = pyqtSignal()

    def __init__(self, text='', parent=None, isSendEventToParent: bool = True):
        super().__init__(text, parent)
        self.isSendEventToParent = isSendEventToParent
        # 储存原始的text
        self.rawText = text
        self.customToolTip = None

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

    def setCustomToolTip(self, toolTip, toolTipText: str):
        """ 设置提示条和提示条出现的位置 """
        self.customToolTip = toolTip
        self.customToolTipText = toolTipText

    def enterEvent(self, e: QEnterEvent):
        """ 如果有设置提示条的话就显示提示条 """
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            # 有折叠发生时需要再加一个偏移量
            self.customToolTip.move(
                e.globalX() - int(self.customToolTip.width() / 2),
                e.globalY() - 100 - self.customToolTip.isWordWrap * 30)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 判断鼠标是否离开标签 """
        if self.parent() and self.customToolTip:
            notLeave = isNotLeave(self)
            if notLeave:
                return
            self.customToolTip.hide()


class ErrorIcon(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置提示条
        self.customToolTip = None
        self.setPixmap(
            QPixmap('resource\\images\\empty_lineEdit_error.png'))
        self.setFixedSize(21, 21)

    def setCustomToolTip(self, toolTip, text: str):
        """ 设置提示条和提示条内容 """
        self.customToolTip = toolTip
        self.customToolTipText = text

    def enterEvent(self, e):
        """ 鼠标进入时显示提示条 """
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            # 有折叠发生时需要再加一个偏移量
            self.customToolTip.move(
                e.globalX() - int(self.customToolTip.width() / 2),
                e.globalY() - 100 - self.customToolTip.isWordWrap * 30)
            self.customToolTip.show()
            self.hasEnter = True

    def leaveEvent(self, e):
        """ 判断鼠标是否离开标签 """
        if self.parent() and self.customToolTip:
            notLeave = isNotLeave(self)
            if notLeave:
                return
            self.customToolTip.hide()

