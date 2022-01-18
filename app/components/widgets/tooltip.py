# coding:utf-8
from PyQt5.QtCore import QFile, QPropertyAnimation
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QFrame


class Tooltip(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.text = text
        self.hBox = QHBoxLayout(self)
        self.label = QLabel(text, self)
        self.ani = QPropertyAnimation(self, b'windowOpacity', self)

        # 设置布局
        self.hBox.addWidget(self.label)
        self.hBox.setContentsMargins(10, 7, 10, 7)

        # 设置阴影
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(32)
        self.shadowEffect.setColor(QColor(0, 0, 0, 60))
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)

        # 设置层叠样式
        self.__setQss()

    def setText(self, text: str):
        """ 设置文本 """
        self.text = text
        self.label.setText(text)
        self.label.adjustSize()
        self.adjustSize()

    def __setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/tooltip.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.label.adjustSize()
        self.adjustSize()