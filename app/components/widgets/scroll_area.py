# coding:utf-8
from collections import deque
from enum import Enum
from math import cos, pi

from PyQt5.QtCore import QDateTime, Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal
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

        update: bool
            whether to trigger the enter/leave event when scrolling
        """
        super().__init__(parent)
        self.fps = 60
        self.duration = 400
        self.stepsTotal = 0
        self.stepRatio = 1.5
        self.acceleration = 1
        self.lastWheelEvent = None
        self.scrollStamps = deque()
        self.stepsLeftQueue = deque()
        self.smoothMoveTimer = QTimer(self)
        self.smoothMode = SmoothMode(SmoothMode.COSINE)
        self.smoothMoveTimer.timeout.connect(self.__smoothMove)

        if trigger:
            self.verticalScrollBar().valueChanged.connect(self.__fakeMoveMouse)

    def __fakeMoveMouse(self):
        """ fake move mouse """
        QCursor.setPos(QCursor.pos() + QPoint(0, 1))
        QApplication.processEvents()
        QCursor.setPos(QCursor.pos() - QPoint(0, 1))

    def setSmoothMode(self, smoothMode):
        """ set smooth mode """
        self.smoothMode = smoothMode

    def wheelEvent(self, e: QWheelEvent):
        if self.smoothMode == SmoothMode.NO_SMOOTH:
            super().wheelEvent(e)
            return

        # push current time to queque
        now = QDateTime.currentDateTime().toMSecsSinceEpoch()
        self.scrollStamps.append(now)
        while now - self.scrollStamps[0] > 500:
            self.scrollStamps.popleft()

        # adjust the acceration ratio based on unprocessed events
        accerationRatio = min(len(self.scrollStamps) / 15, 1)
        if not self.lastWheelEvent:
            self.lastWheelEvent = QWheelEvent(e)
        else:
            self.lastWheelEvent = e

        # get the number of steps
        self.stepsTotal = self.fps * self.duration / 1000

        # get the moving distance corresponding to each event
        delta = e.angleDelta().y() * self.stepRatio
        if self.acceleration > 0:
            delta += delta * self.acceleration * accerationRatio

        # form a list of moving distances and steps, and insert it into the queue for processing.
        self.stepsLeftQueue.append([delta, self.stepsTotal])

        # overflow time of timer: 1000ms/frames
        self.smoothMoveTimer.start(1000 / self.fps)

    def __smoothMove(self):
        """ 计时器溢出时进行平滑滚动 """
        totalDelta = 0

        # Calculate the scrolling distance of all unprocessed events,
        # the timer will reduce the number of steps by 1 each time it overflows.
        for i in self.stepsLeftQueue:
            totalDelta += self.__subDelta(i[0], i[1])
            i[1] -= 1

        # If the event has been processed, move it out of the queue
        while self.stepsLeftQueue and self.stepsLeftQueue[0][1] == 0:
            self.stepsLeftQueue.popleft()

        # create wheel event
        e = QWheelEvent(
            self.lastWheelEvent.pos(),
            self.lastWheelEvent.globalPos(),
            QPoint(),
            QPoint(0, totalDelta),
            round(totalDelta),
            Qt.Vertical,
            self.lastWheelEvent.buttons(),
            Qt.NoModifier
        )

        # send wheel event to app
        QApplication.sendEvent(self.verticalScrollBar(), e)

        # stop scrolling if the queque is empty
        if not self.stepsLeftQueue:
            self.smoothMoveTimer.stop()

    def __subDelta(self, delta, stepsLeft):
        """ get the interpolation for each step """
        m = self.stepsTotal / 2
        x = abs(self.stepsTotal - stepsLeft - m)

        res = 0
        if self.smoothMode == SmoothMode.NO_SMOOTH:
            res = 0
        elif self.smoothMode == SmoothMode.CONSTANT:
            res = delta / self.stepsTotal
        elif self.smoothMode == SmoothMode.LINEAR:
            res = 2 * delta / self.stepsTotal * (m - x) / m
        elif self.smoothMode == SmoothMode.QUADRATI:
            res = 3 / 4 / m * (1 - x * x / m / m) * delta
        elif self.smoothMode == SmoothMode.COSINE:
            res = (cos(x * pi / m) + 1) / (2 * m) * delta

        return res


class SmoothMode(Enum):
    """ Smooth mode """
    NO_SMOOTH = 0
    CONSTANT = 1
    LINEAR = 2
    QUADRATI = 3
    COSINE = 4


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
        self.ani.finished.connect(self.__onScrollFinished)

    def __onScrollFinished(self):
        self.scrollFinished.emit()
        return

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vScrollBar = SmoothScrollBar()
        self.vScrollBar.setOrientation(Qt.Vertical)
        self.setVerticalScrollBar(self.vScrollBar)

    def wheelEvent(self, e: QWheelEvent):
        self.vScrollBar.scrollValue(-e.angleDelta().y())
