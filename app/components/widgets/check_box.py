# coding:utf-8

from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QCheckBox


class CheckBox(QCheckBox):
    """ 可以转发点击消息的复选框 """

    def __init__(self, parent=None, text="", forwardTargetWidget=None):
        """ 实例化复选框

        Parameters
        ----------
        parent:
            父级窗口

        text: str
            复选框的文字

        forwardTargetWidget:
            转发鼠标点击消息的目的小部件
        """
        super().__init__(parent)
        self.setText(text)
        self.forwardTargetWidget = forwardTargetWidget

    def setForwardTargetWidget(self, widget):
        """ 设置转发目的地小部件 """
        self.forwardTargetWidget = widget

    def mousePressEvent(self, e: QMouseEvent):
        """ 转发鼠标点击事件给目标小部件 """
        super().mousePressEvent(e)
        if not self.forwardTargetWidget:
            return
        e = QMouseEvent(
            QEvent.MouseButtonPress,
            QPoint(
                e.pos().x() + self.x() - self.forwardTargetWidget.x(),
                e.pos().y() + self.y() - self.forwardTargetWidget.y(),
            ),
            e.globalPos(),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        QApplication.sendEvent(self.forwardTargetWidget, e)

    def mouseReleaseEvent(self, e):
        """ 鼠标松开转发事件 """
        super().mouseReleaseEvent(e)
        if self.forwardTargetWidget:
            QApplication.sendEvent(self.forwardTargetWidget, e)
