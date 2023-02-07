# coding:utf-8
from common.smooth_scroll import SmoothScroll, SmoothMode
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QWheelEvent, QCursor
from PyQt5.QtWidgets import QApplication, QScrollArea, QScrollBar


class ScrollArea(QScrollArea):
    """ A scroll area which can scroll smoothly """

    def __init__(self, parent=None, trigger=False):
        """
        Parameters
        ----------
        parent: QWidget
            parent window

        trigger: bool
            whether to trigger the enter/leave event when scrolling
        """
        super().__init__(parent)
        self.smoothScroll = SmoothScroll(self)
        self.smoothScroll.setSmoothMode(SmoothMode.COSINE)

        if trigger:
            self.verticalScrollBar().valueChanged.connect(self.__fakeMoveMouse)

    def __fakeMoveMouse(self):
        """ fake move mouse """
        QCursor.setPos(QCursor.pos() + QPoint(0, 1))
        QApplication.processEvents()
        QCursor.setPos(QCursor.pos() - QPoint(0, 1))

    def wheelEvent(self, e):
        self.smoothScroll.wheelEvent(e)


class SmoothScrollBar(QScrollBar):
    """ Smooth scroll bar """

    scrollFinished = pyqtSignal()

    def __init__(self, parent=None):
        QScrollBar.__init__(self, parent)
        self.ani = QPropertyAnimation()
        self.ani.setTargetObject(self)
        self.ani.setPropertyName(b"value")
        self.ani.setEasingCurve(QEasingCurve.OutCubic)
        self.ani.setDuration(500)
        self.__value = self.value()
        self.ani.finished.connect(self.scrollFinished)

    def setValue(self, value: int):
        if value == self.value():
            return

        # stop running animation
        self.ani.stop()
        self.scrollFinished.emit()

        self.ani.setStartValue(self.value())
        self.ani.setEndValue(value)
        self.ani.start()

    def scrollValue(self, value: int):
        """ scroll the specified distance """
        self.__value += value
        self.__value = max(self.minimum(), self.__value)
        self.__value = min(self.maximum(), self.__value)
        self.setValue(self.__value)

    def scrollTo(self, value: int):
        """ scroll to the specified position """
        self.__value = value
        self.__value = max(self.minimum(), self.__value)
        self.__value = min(self.maximum(), self.__value)
        self.setValue(self.__value)

    def resetValue(self, value):
        self.__value = value

    def mousePressEvent(self, e):
        self.ani.stop()
        super().mousePressEvent(e)
        self.__value = self.value()

    def mouseReleaseEvent(self, e):
        self.ani.stop()
        super().mouseReleaseEvent(e)
        self.__value = self.value()

    def mouseMoveEvent(self, e):
        self.ani.stop()
        super().mouseMoveEvent(e)
        self.__value = self.value()


class SmoothScrollArea(QScrollArea):
    """ Smooth scroll area """

    def __init__(self, parent=None, trigger=False):
        """
        Parameters
        ----------
        parent: QWidget
            parent window

        trigger: bool
            whether to trigger the enter/leave event when scrolling
        """
        super().__init__(parent)
        self.vScrollBar = SmoothScrollBar()
        self.vScrollBar.setOrientation(Qt.Vertical)
        self.setVerticalScrollBar(self.vScrollBar)

        if trigger:
            self.verticalScrollBar().valueChanged.connect(self.__fakeMoveMouse)

    def wheelEvent(self, e: QWheelEvent):
        self.vScrollBar.scrollValue(-e.angleDelta().y())

    def __fakeMoveMouse(self):
        """ fake move mouse """
        QCursor.setPos(QCursor.pos() + QPoint(0, 1))
        QApplication.processEvents()
        QCursor.setPos(QCursor.pos() - QPoint(0, 1))
