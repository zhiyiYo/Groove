# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout


class HBoxLayout(QHBoxLayout):
    """ Horizontal box layout """

    def __init__(self, parent):
        super().__init__(parent)
        self.__widget_list = []

    def addWidget(self, widget, stretch=0, alignment=Qt.AlignLeft):
        """ add widget to layout """
        super().addWidget(widget, stretch, alignment)
        self.__widget_list.append(widget)

    def removeWidget(self, widget):
        """ remove widget from layout """
        super().removeWidget(widget)
        self.__widget_list.remove(widget)

    def removeAllWidget(self):
        """ remove all widgets from layout """
        for widget in self.__widget_list:
            super().removeWidget(widget)

        self.__widget_list.clear()

    def widgets(self) -> list:
        return self.__widget_list
