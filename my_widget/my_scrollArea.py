import sys

from PyQt5.QtCore import (
    QAbstractAnimation, QEasingCurve, QPropertyAnimation, Qt)
from PyQt5.QtWidgets import QScrollArea


class ScrollArea(QScrollArea):
    """ 一个可以平滑滚动的区域 """
    def __init__(self, parent=None):
        super().__init__(parent)

        # 实例化动画效果
        self.animation = QPropertyAnimation(self.verticalScrollBar(), b'value')
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

    def wheelEvent(self, e):
        """ 实现平滑滚动效果 """
        preValue = self.verticalScrollBar().value()
        deltaValue = int(e.angleDelta().y() / 120 * 3 * self.scrollStep)
        newValue = preValue - deltaValue
        if self.animation.state() == QAbstractAnimation.Stopped:
            self.animation.setStartValue(self.verticalScrollBar().value())
            self.animation.setEndValue(newValue)
            # 开始滚动
            self.animation.start()
        else:
            self.verticalScrollBar().setValue(self.animation.endValue())
            self.animation.stop()
            self.animation.setStartValue(self.verticalScrollBar().value())
            self.animation.setEndValue(newValue)
            self.animation.start()
