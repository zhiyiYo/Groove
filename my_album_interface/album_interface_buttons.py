# coding:utf-8

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
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        # 计算文本宽度
        self.__getTextWidth()
        if self.text:
            self.setFixedSize(self.textWidth + 70, 46)
        else:
            self.setFixedSize(60, 46)
        # 安装事件过滤器
        self.installEventFilter(self)

    def __getTextWidth(self):
        """ 计算按钮文本的宽度 """
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 10))
        self.textWidth = fontMetrics.width(self.text)

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
            brush = QBrush(QColor(255, 255, 255, 127)) # 50%不透明度
            painter.setBrush(brush)
            painter.drawRoundedRect(self.rect(), 23, 23)
        elif self.isEnter:
            brush = QBrush(QColor(255, 255, 255, 51)) # 20%不透明度
            painter.setBrush(brush)
            painter.drawRoundedRect(self.rect(), 23, 23)
        # 绘制图标和文字
        painter.drawPixmap(20, 13, self.__iconPixmap.width(),
                           self.__iconPixmap.height(), self.__iconPixmap)
        painter.setPen(Qt.white)
        painter.setFont(QFont('Microsoft YaHei', 10))
        painter.drawText(50, 29, self.text)


