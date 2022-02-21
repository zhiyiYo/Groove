# coding:utf-8

from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QCheckBox


class CheckBox(QCheckBox):
    """ A check box that can forward click signal """

    def __init__(self, parent=None, text="", forwardTargetWidget=None):
        """
        Parameters
        ----------
        parent:
            parent window

        text: str
            text of check box

        forwardTargetWidget:
            the widget to receive signal
        """
        super().__init__(parent)
        self.setText(text)
        self.forwardTargetWidget = forwardTargetWidget

    def setForwardTargetWidget(self, widget):
        """ set the widget to receive signal """
        self.forwardTargetWidget = widget

    def mousePressEvent(self, e: QMouseEvent):
        if not self.forwardTargetWidget:
            super().mousePressEvent(e)
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
        if self.forwardTargetWidget:
            QApplication.sendEvent(self.forwardTargetWidget, e)
        else:
            super().mouseReleaseEvent(e)

