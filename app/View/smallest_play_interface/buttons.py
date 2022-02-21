# coding:utf-8
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt5.QtWidgets import QToolButton


class SmallestPlayModeButton(QToolButton):
    """ Smallest interface button """

    def __init__(self, iconPath, parent=None, buttonSize: tuple = (45, 45)):
        super().__init__(parent)
        self.__isEnter = False
        self.__isPressed = False
        self._pixPos_list = [(1, 0), (2, 2)]
        self.iconPixmap = QPixmap(iconPath)

        self.resize(*buttonSize)
        self.setStyleSheet(
            "QToolButton{border:none;margin:0;background:transparent}")
        self.installEventFilter(self)

    def eventFilter(self, obj, e: QEvent):
        if obj == self:
            if e.type() == QEvent.Enter:
                self.__isEnter = True
                self.update()
                return False
            elif e.type() == QEvent.Leave:
                self.__isEnter = False
                self.update()
                return False
            elif e.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonDblClick, QEvent.MouseButtonRelease]:
                self.__isPressed = not self.__isPressed
                self.update()
                return False

        return super().eventFilter(obj, e)

    def paintEvent(self, e):
        """ paint button """
        iconPixmap = self.iconPixmap
        px, py = self._pixPos_list[0]
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        pen = Qt.NoPen
        if self.__isPressed:
            pen = QPen(QColor(255, 255, 255, 30))
            pen.setWidth(2)
            iconPixmap = self.iconPixmap.scaled(
                self.iconPixmap.width() - 4, self.iconPixmap.height() - 4,
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            px, py = self._pixPos_list[1]
        elif self.__isEnter:
            pen = QPen(QColor(255, 255, 255, 96))
            pen.setWidth(2)
        painter.setPen(pen)

        painter.drawEllipse(1, 1, self.width()-2, self.height()-2)
        painter.drawPixmap(px, py, iconPixmap.width(),
                           iconPixmap.height(), iconPixmap)


class PlayButton(SmallestPlayModeButton):
    """ Play button """

    def __init__(self, iconPaths: list, parent=None, buttonSize=(45, 45), isPause=True):
        super().__init__(iconPaths[isPause], parent, buttonSize)
        self.__isPause = isPause
        self.iconPixmaps = [QPixmap(iconPath) for iconPath in iconPaths]
        self._pixPos_list = [(0, 0), (2, 2)]

    def mouseReleaseEvent(self, e):
        self.setPlay(self.__isPause)
        super().mouseReleaseEvent(e)

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.__isPause = not isPlay
        self.iconPixmap = self.iconPixmaps[self.__isPause]
        self.update()