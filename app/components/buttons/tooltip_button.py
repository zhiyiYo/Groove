# coding:utf-8
from components.widgets.tooltip import Tooltip
from PyQt5.QtCore import QEvent, QObject, QPoint
from PyQt5.QtWidgets import QToolButton, QPushButton


class TooltipButton(QToolButton):
    """ Tool button with a tooltip """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
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
        if self.__tooltip.text != self.toolTip():
            self.__tooltip.setText(self.toolTip())

        # the tooltip must be moved outside the button area
        pos = self.mapTo(self.window(), QPoint(0, 0))
        x = pos.x() + self.width()//2 - self.__tooltip.width()//2
        y = pos.y() - 2 - self.__tooltip.height()

        # adjust postion to prevent tooltips from appearing outside the window
        x = min(max(5, x), self.window().width() - self.__tooltip.width() - 5)

        self.__tooltip.move(x, y)
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
        if self.__tooltip.text != self.toolTip():
            self.__tooltip.setText(self.toolTip())

        # the tooltip must be moved outside the button area
        pos = self.mapTo(self.window(), QPoint(0, 0))
        x = pos.x() + self.width()//2 - self.__tooltip.width()//2
        y = pos.y() - 2 - self.__tooltip.height()

        # adjust postion to prevent tooltips from appearing outside the window
        x = min(max(5, x), self.window().width() - self.__tooltip.width() - 5)

        self.__tooltip.move(x, y)
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
