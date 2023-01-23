# coding:utf-8

from common.get_pressed_pos import getPressedPos, Position
from common.image_utils import PixmapPerspectiveTransform
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtWidgets import QPushButton


class PerspectivePushButton(QPushButton):
    """ A push button which can apply perspective transform when clicked """

    def __init__(self, text: str = "", parent=None, icon: QIcon = None):
        super().__init__(text, parent)
        self.transform = PixmapPerspectiveTransform()
        self.__pressedPix = None
        self.__pressedPos = None
        if icon:
            self.setIcon(icon)

    def mousePressEvent(self, e):
        """ apply perspective transform """
        super().mousePressEvent(e)

        # grab screen
        self.grabMouse()
        self.transform.setPixmap(self.grab())

        # get pressed pos
        self.__pressedPos = getPressedPos(self, e)

        # get destination corner coordinates after transform
        w = self.transform.width
        h = self.transform.height
        dstPointMap = {
            Position.LEFT: [[3, 1], [w - 2, 1], [3, h - 2], [w - 2, h - 1]],
            Position.TOP_LEFT: [[3, 2], [w - 1, 1], [1, h - 2], [w - 2, h - 1]],
            Position.BOTTOM_LEFT: [[3, 1], [w - 2, 1], [3, h - 3], [w - 1, h - 1]],
            Position.CENTER: [[2, 2], [w - 3, 2], [2, h - 3], [w - 3, h - 3]],
            Position.TOP: [[2, 2], [w - 3, 2], [1, h - 2], [w - 2, h - 2]],
            Position.BOTTOM: [[1, 1], [w - 2, 1], [3, h - 3], [w - 4, h - 3]],
            Position.BOTTOM_RIGHT: [[1, 1], [w - 2, 1], [0, h - 1], [w - 4, h - 3]],
            Position.TOP_RIGHT: [[0, 0], [w - 4, 1], [1, h - 1], [w - 2, h - 2]],
            Position.RIGHT: [[1, 0], [w - 4, 1], [1, h - 1], [w - 4, h - 2]],
        }

        if self.__pressedPos in dstPointMap:
            self.transform.setDstPoints(*dstPointMap[self.pressedPos])

        self.__pressedPix = self.transform.getPerspectiveTransform(w, h).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.update()

    def mouseReleaseEvent(self, e):
        """ show all widgets """
        self.releaseMouse()
        self.__pressedPos = None
        # self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        """ paint button """
        if not self.__pressedPos:
            super().paintEvent(e)
            return

        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing
            | QPainter.HighQualityAntialiasing
            | QPainter.SmoothPixmapTransform
        )
        painter.setPen(Qt.NoPen)

        # paint background
        painter.drawPixmap(self.rect(), self.__pressedPix)

    @property
    def pressedPos(self):
        """ get mouse pressed pos """
        return self.__pressedPos
