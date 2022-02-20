# coding:utf-8
from .tooltip_button import TooltipButton
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPainter, QPixmap, QBrush, QColor
from PyQt5.QtWidgets import QToolButton


class CircleButton(TooltipButton):
    """ Circle button """

    def __init__(self, iconPath: str, parent=None, iconSize: tuple = (47, 47), buttonSize: tuple = (47, 47)):
        super().__init__(parent)
        self.iconWidth, self.iconHeight = iconSize
        self.iconPixmap = QPixmap(iconPath)
        self.isEnter = False
        self.isPressed = False

        # control paint position
        self._pixPos_list = [(1, 0), (2, 2)]

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(*buttonSize)
        self.setStyleSheet(
            "QToolButton{border:none;margin:0;background:transparent}")
        self.installEventFilter(self)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.hideToolTip()

    def eventFilter(self, obj, e: QEvent):
        if obj == self:
            if e.type() == QEvent.Enter:
                self.isEnter = True
                self.update()
                return False
            elif e.type() == QEvent.Leave:
                self.isEnter = False
                self.update()
                return False
            elif e.type() in [
                QEvent.MouseButtonPress,
                QEvent.MouseButtonDblClick,
                QEvent.MouseButtonRelease,
            ]:
                self.isPressed = not self.isPressed
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
        painter.setPen(Qt.NoPen)

        if self.isPressed:
            brush = QBrush(QColor(255, 255, 255, 70))
            painter.setBrush(brush)
            painter.drawEllipse(0, 0, self.iconWidth, self.iconHeight)
            iconPixmap = self.iconPixmap.scaled(
                self.iconPixmap.width() - 4,
                self.iconPixmap.height() - 4,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            px, py = self._pixPos_list[1]
        elif self.isEnter:
            painter.setOpacity(0.5)

        # paint icon
        painter.drawPixmap(px, py, iconPixmap.width(),
                           iconPixmap.height(), iconPixmap)
