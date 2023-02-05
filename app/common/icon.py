# coding:utf-8
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, QRectF
from PyQt5.QtGui import QIcon, QIconEngine, QImage, QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer

from .config import config, Theme


class PixmapIconEngine(QIconEngine):
    """ Pixmap icon engine """

    def __init__(self, iconPath: str):
        self.iconPath = iconPath
        super().__init__()

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State):
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.drawImage(rect, QImage(self.iconPath))

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        self.paint(QPainter(pixmap), QRect(QPoint(0, 0), size), mode, state)
        return pixmap


class Icon(QIcon):

    def __init__(self, iconPath: str):
        self.iconPath = iconPath
        super().__init__(PixmapIconEngine(iconPath))


class MenuIconEngine(QIconEngine):

    def __init__(self, icon: QIcon):
        super().__init__()
        self.icon = icon

    def paint(self, painter, rect, mode, state):
        self.icon.paint(painter, rect, Qt.AlignHCenter, QIcon.Normal, state)


def getIconColor():
    """ get the color of icon based on theme """
    return "white" if config.theme == Theme.DARK else 'black'


def drawSvgIcon(iconPath, painter, rect):
    """ draw svg icon

    Parameters
    ----------
    iconPath: str
        the path of svg icon

    painter: QPainter
        painter

    rect: QRect | QRectF
        the rect to render icon
    """
    renderer = QSvgRenderer(iconPath)
    renderer.render(painter, QRectF(rect))
