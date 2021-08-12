# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout


class HBoxLayout(QHBoxLayout):
    """ 水平布局 """

    def __init__(self, parent):
        super().__init__(parent)
        self.__widget_list = []

    def addWidget(self, widget, stretch=0, alignment=Qt.AlignLeft):
        """ 向布局中添加小部件 """
        super().addWidget(widget, stretch, alignment)
        self.__widget_list.append(widget)

    def removeWidget(self, widget):
        """ 从布局中移除小部件 """
        super().removeWidget(widget)
        self.__widget_list.remove(widget)

    def removeAllWidget(self):
        """ 从布局中移除所有小部件 """
        for widget in self.__widget_list:
            super().removeWidget(widget)
        self.__widget_list.clear()

    def widgets(self) -> list:
        """ 返回小部件列表 """
        return self.__widget_list
