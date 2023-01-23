# coding:utf-8
from common.get_pressed_pos import getPressedPos, Position
from common.image_utils import PixmapPerspectiveTransform
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPainter, QPixmap, QScreen
from PyQt5.QtWidgets import QApplication, QWidget


class PerspectiveWidget(QWidget):
    """ A widget which can apply perspective transform when clicked """

    def __init__(self, parent=None, isTransScreenshot=False):
        super().__init__(parent)
        self.__visibleChildren = []
        self.__isTransScreenshot = isTransScreenshot
        self.__perspectiveTrans = PixmapPerspectiveTransform()
        self.__screenshotPix = None
        self.__pressedPix = None
        self.__pressedPos = None
        self.__isPressed = False

    @property
    def pressedPos(self) -> str:
        return self.__pressedPos

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if self.__pressedPos:
            return

        self.__isPressed = True

        # grab screen
        self.grabMouse()
        pixmap = self.grab()
        self.__perspectiveTrans.setPixmap(pixmap)

        # get destination corner coordinates after transform
        self.__setDstPointsByPressedPos(getPressedPos(self, e))

        self.__pressedPix = self.__getTransformPixmap()

        if self.__isTransScreenshot:
            self.__adjustTransformPix()

        # 隐藏本来看得见的小部件
        self.__visibleChildren = [
            i for i in self.children() if hasattr(i, "isVisible") and i.isVisible()]

        for child in self.__visibleChildren:
            if hasattr(child, "hide"):
                child.hide()

        self.update()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.releaseMouse()

        if not self.__isPressed:
            return

        self.__isPressed = False
        self.__pressedPos = None
        self.update()

        for child in self.__visibleChildren:
            if hasattr(child, "show"):
                child.show()

    def paintEvent(self, e):
        """ paint widget """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing
            | QPainter.HighQualityAntialiasing
            | QPainter.SmoothPixmapTransform
        )
        painter.setPen(Qt.NoPen)

        # paint perspective transformed image
        if self.__pressedPos:
            painter.drawPixmap(self.rect(), self.__pressedPix)

    def __setDstPointsByPressedPos(self, pressedPos: str):
        """ get destination corner coordinates after transform """
        self.__pressedPos = pressedPos
        w = self.__perspectiveTrans.width
        h = self.__perspectiveTrans.height
        dstPointMap = {
            Position.LEFT: [[5, 4], [w - 2, 1], [3, h - 3], [w - 2, h - 1]],
            Position.TOP_LEFT: [[7, 6], [w - 1, 1], [1, h - 2], [w - 2, h - 1]],
            Position.BOTTOM_LEFT: [[0, 1], [w - 3, 0], [6, h - 5], [w - 2, h - 2]],
            Position.CENTER: [[3, 4], [w - 4, 4], [3, h - 3], [w - 4, h - 3]],
            Position.TOP: [[4, 5], [w - 5, 5], [0, h - 1], [w - 1, h - 1]],
            Position.BOTTOM: [[0, 0], [w - 1, 0], [4, h - 4], [w - 5, h - 4]],
            Position.BOTTOM_RIGHT: [[1, 0], [w - 3, 2], [1, h - 2], [w - 6, h - 5]],
            Position.TOP_RIGHT: [[0, 1], [w - 7, 5], [2, h - 1], [w - 2, h - 2]],
            Position.RIGHT: [[1, 1], [w - 6, 4], [2, h - 1], [w - 4, h - 3]]
        }
        self.__perspectiveTrans.setDstPoints(*dstPointMap[pressedPos])

    def __getTransformPixmap(self) -> QPixmap:
        """ get the image of window after transformed """
        pix = self.__perspectiveTrans.getPerspectiveTransform(
            self.__perspectiveTrans.width, self.__perspectiveTrans.height
        ).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return pix

    def __getScreenShot(self) -> QPixmap:
        """ get screen shot """
        screen = QApplication.primaryScreen()  # type:QScreen
        pos = self.mapToGlobal(QPoint(0, 0))  # type:QPoint
        pix = screen.grabWindow(0, pos.x(), pos.y(),
                                self.width(), self.height())
        return pix

    def __adjustTransformPix(self):
        """ adjust transform pixmap to elimate black edge """
        self.__screenshotPix = self.__getScreenShot()
        self.__perspectiveTrans.setPixmap(self.__screenshotPix)
        self.__screenshotPressedPix = self.__getTransformPixmap()

        img_1 = self.__perspectiveTrans.transQPixmapToNdarray(
            self.__pressedPix)
        img_2 = self.__perspectiveTrans.transQPixmapToNdarray(
            self.__screenshotPressedPix)

        mask = img_1[:, :, -1] == 0
        img_2[mask] = img_1[mask]
        self.__pressedPix = self.__perspectiveTrans.transNdarrayToQPixmap(
            img_2)
