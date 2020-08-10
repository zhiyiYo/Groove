# coding:utf-8

import sys

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import (QBrush, QColor, QFont, QFontMetrics, QPainter, QPen,
                         QPixmap)
from PyQt5.QtWidgets import QApplication, QPushButton,QWidget


class BasicButton(QPushButton):
    """ 专辑界面信息栏按钮 """

    def __init__(self, iconPath, text, parent=None):
        super().__init__(parent=parent)
        self.iconPath = iconPath
        self.text = text
        self.__iconPixmap = QPixmap(iconPath)
        # 设置标志位
        self.isPressed = False
        self.isEnter = False
        # 计算文本宽度
        self.__getTextWidth()
        self.setFixedSize(self.textWidth + 70, 46)
        # 安装事件过滤器
        self.installEventFilter(self)

    def __getTextWidth(self):
        """ 计算按钮文本的宽度 """
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 10))
        self.textWidth = sum([fontMetrics.width(i) for i in self.text])

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.isEnter = True
                self.update()
            elif e.type() == QEvent.Leave:
                self.isEnter = False
                self.update()
            elif e.type() == QEvent.MouseButtonPress:
                self.isPressed = True
                self.update()
            elif e.type() == QEvent.MouseButtonRelease:
                self.isPressed = False
                self.update()
        return super().eventFilter(obj, e)

    def paintEvent(self, e):
        """ 绘制图标和文本 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        # 绘制背景
        if self.isPressed:
            brush = QBrush(QColor(255, 255, 255, 130))
            painter.setBrush(brush)
            painter.drawRoundedRect(self.rect(), 23, 23)
        elif self.isEnter:
            brush = QBrush(QColor(255, 255, 255, 70))
            painter.setBrush(brush)
            painter.drawRoundedRect(self.rect(), 23, 23)
        # 绘制图标和文字
        painter.drawPixmap(20, 13, self.__iconPixmap.width(),
                           self.__iconPixmap.height(), self.__iconPixmap)
        painter.setPen(Qt.white)
        painter.setFont(QFont('Microsoft YaHei', 10))
        painter.drawText(50, 29, self.text)


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.bt = BasicButton(
            r'resource\images\album_interface\固定到开始菜单.png', '固定到"开始"菜单',self)
        self.setStyleSheet('QWidget{background:#404c59}')
        self.resize(200, 200)
        self.bt.move(41,77)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
