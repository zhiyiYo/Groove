# coding:utf-8

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPen, QPolygon
from PyQt5.QtWidgets import QWidget

from app.common.get_pressed_pos import getPressedPos


class FoldingWindow(QWidget):
    """ 点击不同方位翻折效果不同的窗口 """

    # 创建点击信号
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(365, 90)
        # 设置标志位
        self.pressedPos = None
        self.isEnter = False

    def enterEvent(self, e):
        """ 鼠标进入界面就置位进入标志位 """
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        """ 鼠标离开就清零置位标志位 """
        self.isEnter = False
        self.update()

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时更新界面 """
        self.pressedPos = None
        self.update()
        if e.button() == Qt.LeftButton:
            self.clicked.emit()

    def mousePressEvent(self, e: QMouseEvent):
        """ 根据鼠标的不同按下位置更新标志位 """
        self.pressedPos = getPressedPos(self, e)
        self.update()

    def paintEvent(self, e):
        """ 根据不同的情况绘制不同的背景 """
        # super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        brush = QBrush(QColor(204, 204, 204))
        painter.setPen(Qt.NoPen)
        if not self.isEnter:
            painter.setBrush(brush)
            painter.drawRoundedRect(self.rect(), 5, 5)
        else:
            painter.setPen(QPen(QColor(204, 204, 204), 2))
            painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
            painter.setPen(Qt.NoPen)
            if not self.pressedPos:
                brush.setColor(QColor(230, 230, 230))
                painter.setBrush(brush)
                painter.drawRect(2, 2, self.width() - 4, self.height() - 4)
            else:
                brush.setColor(QColor(153, 153, 153))
                painter.setBrush(brush)
                # 左上角
                if self.pressedPos == "left-top":
                    points = [
                        QPoint(6, 2),
                        QPoint(self.width() - 1, 1),
                        QPoint(self.width() - 1, self.height() - 1),
                        QPoint(1, self.height() - 1),
                    ]
                    painter.drawPolygon(QPolygon(points), 4)
                # 左边
                elif self.pressedPos == "left":
                    painter.drawRoundedRect(
                        6, 1, self.width() - 7, self.height() - 2, 3, 3
                    )
                # 左下角
                elif self.pressedPos == "left-bottom":
                    points = [
                        QPoint(1, 1),
                        QPoint(self.width() - 1, 1),
                        QPoint(self.width() - 1, self.height() - 1),
                        QPoint(6, self.height() - 2),
                    ]
                    painter.drawPolygon(QPolygon(points), 4)
                # 顶部
                elif self.pressedPos == "top":
                    points = [
                        QPoint(6, 2),
                        QPoint(self.width() - 6, 2),
                        QPoint(self.width() - 1, self.height() - 1),
                        QPoint(1, self.height() - 1),
                    ]
                    painter.drawPolygon(QPolygon(points), 4)
                # 中间
                elif self.pressedPos == "center":
                    painter.drawRoundedRect(
                        6, 1, self.width() - 12, self.height() - 2, 3, 3
                    )
                # 底部
                elif self.pressedPos == "bottom":
                    points = [
                        QPoint(1, 1),
                        QPoint(self.width() - 1, 1),
                        QPoint(self.width() - 6, self.height() - 2),
                        QPoint(6, self.height() - 2),
                    ]
                    painter.drawPolygon(QPolygon(points), 4)
                # 右上角
                elif self.pressedPos == "right-top":
                    points = [
                        QPoint(1, 1),
                        QPoint(self.width() - 6, 2),
                        QPoint(self.width() - 1, self.height() - 1),
                        QPoint(1, self.height() - 1),
                    ]
                    painter.drawPolygon(QPolygon(points), 4)
                # 右边
                elif self.pressedPos == "right":
                    painter.drawRoundedRect(
                        1, 1, self.width() - 7, self.height() - 2, 3, 3
                    )
                # 右下角
                elif self.pressedPos == "right-bottom":
                    points = [
                        QPoint(1, 1),
                        QPoint(self.width() - 1, 1),
                        QPoint(self.width() - 6, self.height() - 2),
                        QPoint(1, self.height() - 1),
                    ]
                    painter.drawPolygon(QPolygon(points), 4)
