# coding:utf-8

from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QToolButton


class ThreeStatePushButton(QPushButton):
    """ 三种状态对应三种图标的按钮 """

    def __init__(self, iconPath_dict: dict, text='', iconSize: tuple = (130, 17), parent=None):
        """
        Parameters
        ----------
        iconPath_dict: dict
            图标按钮地址字典，提供 normal、hover 和 pressed 三种状态下的图标地址

        parent:
            父级窗口

        iconSize: tuple
            图标大小
        """
        super().__init__(text, parent)
        self.__iconPath_dict = iconPath_dict
        self.setIcon(QIcon(self.__iconPath_dict['normal']))
        self.setIconSize(QSize(*iconSize))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ 当鼠标移到播放模式按钮上时更换图标 """
        if obj == self:
            if e.type() in [QEvent.Enter, QEvent.HoverMove]:
                self.setIcon(QIcon(self.__iconPath_dict['hover']))
            elif e.type() in [QEvent.Leave, QEvent.MouseButtonRelease]:
                self.setIcon(QIcon(self.__iconPath_dict['normal']))
            elif e.type() == QEvent.MouseButtonPress:
                self.setIcon(QIcon(self.__iconPath_dict['pressed']))
        return False


class ThreeStateButton(QToolButton):
    """ 三种状态对应三种图标的工具按钮 """

    def __init__(self, iconPath_dict: dict, parent=None, icon_size: tuple = (40, 40)):
        """
        Parameters
        ----------
        iconPath_dict: dict
            图标按钮地址字典，提供 normal、hover 和 pressed 三种状态下的图标地址

        parent:
            父级窗口

        iconSize: tuple
            图标大小
        """
        super().__init__(parent)
        # 引用图标地址字典
        self.iconPath_dict = iconPath_dict
        self.resize(icon_size[0], icon_size[1])
        # 初始化小部件
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.setCursor(Qt.ArrowCursor)
        self.setIcon(QIcon(self.iconPath_dict['normal']))
        self.setIconSize(QSize(self.width(), self.height()))
        self.setStyleSheet('border: none; margin: 0px')

    def enterEvent(self, e):
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
