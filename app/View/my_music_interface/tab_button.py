# coding:utf-8

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygon
from PyQt5.QtWidgets import QPushButton

from app.common.get_pressed_pos import getPressedPos


class TabButton(QPushButton):
    """ 标签按钮，点击即可换页 """

    buttonSelected = pyqtSignal(int)

    def __init__(self, text: str, parent=None, tabIndex: int = 0):
        """
        Parameters
        ----------
        text: str
            按钮文本

        parent:
            父级窗口

        tabIndex: int
            按钮对应的标签窗口索引，范围为 `0 ~ N-1`"""
        super().__init__(parent)
        self.text = text
        self.isEnter = False
        self.isSelected = False
        self.pressedPos = None
        self.tabIndex = tabIndex
        self.setFixedSize(55, 40)

    def setSelected(self, isSelected: bool):
        """ 设置选中状态 """
        self.isSelected = isSelected
        self.update()

    def enterEvent(self, e):
        """ 鼠标进入时置位状态位 """
        self.isEnter = True

    def leaveEvent(self, e):
        """ 鼠标进入时清零标志位 """
        self.isEnter = False

    def mousePressEvent(self, e):
        """ 鼠标点击时记录位置 """
        self.pressedPos = getPressedPos(self, e)
        self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """ 鼠标松开更新样式 """
        self.pressedPos = None
        super().mouseReleaseEvent(e)
        self.buttonSelected.emit(self.tabIndex)

    def paintEvent(self, QPaintEvent):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        painter.setFont(QFont("Microsoft YaHei", 15))
        if not self.isSelected:
            self.__paintAllText(painter, 14)
        else:
            self.__paintAllText(painter, 14)
            if not self.pressedPos:
                self.__paintLine(
                    painter,
                    1,
                    self.height() - 3,
                    self.width() - 1,
                    self.height() - 3,
                    self.width() - 1,
                    self.height(),
                    1,
                    self.height(),
                )
            # 左上角和右下角
            elif self.pressedPos in ["left-top", "right-bottom"]:
                self.__paintLine(
                    painter,
                    1,
                    self.height() - 3,
                    self.width() - 1,
                    self.height() - 4,
                    self.width() - 1,
                    self.height() - 1,
                    1,
                    self.height(),
                )
            # 左中右上下
            elif self.pressedPos in ["left", "center", "right", "top", "bottom"]:
                self.__paintLine(
                    painter,
                    2,
                    self.height() - 4,
                    self.width() - 2,
                    self.height() - 4,
                    self.width() - 2,
                    self.height() - 1,
                    2,
                    self.height() - 1,
                )
            # 左下角和右上角
            elif self.pressedPos in ["left-bottom", "right-top"]:
                self.__paintLine(
                    painter,
                    1,
                    self.height() - 4,
                    self.width() - 1,
                    self.height() - 3,
                    self.width() - 1,
                    self.height(),
                    1,
                    self.height() - 1,
                )

    def __paintText(self, painter, shearX, shearY, x=1, y=5):
        """ 绘制文本 """
        painter.shear(shearX, shearY)
        painter.drawText(x, y + 21, self.text)

    def __paintLine(self, painter, x1, y1, x2, y2, x3, y3, x4, y4):
        """ 绘制选中标志 """
        painter.setPen(Qt.NoPen)
        brush = QBrush(QColor(0, 153, 188))
        painter.setBrush(brush)
        points = [QPoint(x1, y1), QPoint(x2, y2), QPoint(x3, y3), QPoint(x4, y4)]
        painter.drawPolygon(QPolygon(points), 4)

    def __paintAllText(self, painter, fontSize=16):
        """ 根据各种点击情况绘制文本 """
        if not self.isSelected:
            pen = QPen(QColor(102, 102, 102))
            painter.setPen(pen)
        if not self.pressedPos:
            if self.isEnter:
                # 鼠标进入时画笔改为黑色
                painter.setPen(QPen(Qt.black))
            self.__paintText(painter, 0, 0)
        else:
            painter.setFont(QFont("Microsoft YaHei", fontSize))
            # 左上角和右下角
            if self.pressedPos in ["left-top", "right-bottom"]:
                self.__paintText(painter, -0.03, 0)
            # 左中右上下
            elif self.pressedPos in ["left", "center", "right", "top", "bottom"]:
                self.__paintText(painter, 0, 0)
            # 左下角和右上角
            elif self.pressedPos in ["left-bottom", "right-top"]:
                self.__paintText(painter, 0.03, 0)

