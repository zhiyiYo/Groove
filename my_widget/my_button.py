# coding:utf-8

""" 自定义按钮库"""


from PyQt5.QtCore import QEvent, QPoint, QSize, Qt, QTimer
from PyQt5.QtGui import (QBrush, QColor, QEnterEvent, QIcon, QPainter, QPen,
                         QPixmap)
from PyQt5.QtWidgets import (QApplication, QGraphicsBlurEffect, QLabel,
                             QPushButton, QToolButton)

from my_functions.is_not_leave import isNotLeave


class RandomPlayButton(QPushButton):
    """ 定义条形随机播放按钮 """

    def __init__(self, text='', slot=None, parent=None):
        super().__init__(text, parent)
        self.setIcon(QIcon('resource\\images\\无序播放所有_130_17.png'))
        self.setIconSize(QSize(130, 17))
        self.setObjectName('randomPlayButton')
        self.clicked.connect(slot)
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ 当鼠标移到播放模式按钮上时更换图标 """
        if obj == self:
            if e.type() in [QEvent.Enter, QEvent.HoverMove]:
                self.setIcon(
                    QIcon('resource\\images\\无序播放所有_hover_130_17.png'))
            elif e.type() in [QEvent.Leave,QEvent.MouseButtonRelease] :
                self.setIcon(QIcon('resource\\images\\无序播放所有_130_17.png'))
            elif e.type() == QEvent.MouseButtonPress:
                self.setIcon(QIcon('resource\\images\\无序播放所有_pressed_130_17.png'))
        return False


class SortModeButton(QPushButton):
    """ 定义排序模式按钮 """

    def __init__(self, text, slot, parent=None):
        super().__init__(text, parent)
        self.setObjectName('sortModeButton')
        self.clicked.connect(slot)


class ThreeStateButton(QToolButton):
    """ 三种状态对应三种图标的按钮，iconPath_dict提供按钮normal、hover、pressed三种状态下的图标地址 """

    def __init__(self, iconPath_dict:dict, parent=None,icon_size:tuple=(40,40)):
        super().__init__(parent)
        # 引用图标地址字典
        self.iconPath_dict = iconPath_dict
        self.resize(icon_size[0],icon_size[1])
        # 初始化小部件
        self.initWidget()
        
    def initWidget(self):
        """ 初始化小部件 """
        self.setCursor(Qt.ArrowCursor)
        self.setIcon(QIcon(self.iconPath_dict['normal']))
        self.setIconSize(QSize(self.width(),self.height()))
        self.setStyleSheet('border: none; margin: 0px')

    def enterEvent(self,e):
        """ hover时更换图标 """
        self.setIcon(QIcon(self.iconPath_dict['hover']))

    def leaveEvent(self, e):
        """ leave时更换图标 """
        self.setIcon(QIcon(self.iconPath_dict['normal']))

    def mousePressEvent(self, e):
        """ 鼠标左键按下时更换图标 """
        if e.button() == Qt.RightButton:
            return
        self.setIcon(QIcon(self.iconPath_dict['pressed']))
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """ 鼠标左键按下时更换图标 """
        if e.button() == Qt.RightButton:
            return
        self.setIcon(QIcon(self.iconPath_dict['normal']))
        super().mouseReleaseEvent(e)