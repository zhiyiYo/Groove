# coding:utf-8
from common.config import config, Theme
from components.widgets.tooltip import Tooltip
from PyQt5.QtCore import QEvent, QObject, QPoint
from PyQt5.QtWidgets import QToolButton, QPushButton


class TooltipButton(QToolButton):
    """ Tool button with a tooltip """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__tooltip = None
        self.__darkTooltip = config.theme == Theme.DARK
        self.installEventFilter(self)

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        if obj is self:
            if e.type() == QEvent.ToolTip:
                return True

        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        super().enterEvent(e)
        if not self.toolTip():
            return

        if self.__tooltip is None:
            self.__tooltip = Tooltip(self.toolTip(), self.window())
            self.__tooltip.setDarkTheme(self.__darkTooltip)

        # update tooltip
        self.__tooltip.setText(self.toolTip())
        self.__tooltip.adjustPos(self.mapTo(self.window(), QPoint()), self.size())
        self.__tooltip.show()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        if self.__tooltip:
            self.__tooltip.hide()

    def hideEvent(self, e):
        super().hideEvent(e)
        if self.__tooltip:
            self.__tooltip.hide()

    def setDarkToolTip(self, dark=False):
        """ set whether to use the dark theme of tooltip """
        self.__darkTooltip = dark

    def hideToolTip(self):
        """ hide tooltip """
        if self.__tooltip:
            self.__tooltip.hide()


class TooltipPushButton(QPushButton):
    """ Push button with a tooltip """

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.__tooltip = None
        self.__darkTooltip = False
        self.installEventFilter(self)

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        if obj is self:
            if e.type() == QEvent.ToolTip:
                return True

        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        super().enterEvent(e)
        if not self.toolTip():
            return

        if self.__tooltip is None:
            self.__tooltip = Tooltip(self.toolTip(), self.window())
            self.__tooltip.setDarkTheme(self.__darkTooltip)

        # update tooltip
        self.__tooltip.setText(self.toolTip())
        self.__tooltip.adjustPos(self.mapTo(self.window(), QPoint()), self.size())
        self.__tooltip.show()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        if self.__tooltip:
            self.__tooltip.hide()

    def hideEvent(self, e):
        super().hideEvent(e)
        if self.__tooltip:
            self.__tooltip.hide()

    def setDarkToolTip(self, dark=False):
        """ set whether to use the dark theme of tooltip """
        self.__darkTooltip = dark

    def hideToolTip(self):
        """ hide tooltip """
        if self.__tooltip:
            self.__tooltip.hide()
