# coding:utf-8
from common.config import config, Theme
from components.widgets.tooltip import ToolTip
from PyQt5.QtCore import QEvent, QObject, QPoint, QTimer
from PyQt5.QtWidgets import QToolButton, QPushButton


class ToolTipButton(QToolButton):
    """ Tool button with a tool tip """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.isEnter = False
        self._tooltip = None
        self._tooltipDelay = 300
        self._isDarkTheme = config.theme == Theme.DARK
        self.timer = QTimer(self)
        self.installEventFilter(self)

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        if obj is self:
            if e.type() == QEvent.ToolTip:
                return True

        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        super().enterEvent(e)
        self.isEnter = True
        if not self.toolTip():
            return

        if self._tooltip is None:
            self._tooltip = ToolTip(self.toolTip(), self.window())
            self._tooltip.setDarkTheme(self._isDarkTheme)

        # update tooltip
        QTimer.singleShot(self._tooltipDelay, self.__showToolTip)

    def __showToolTip(self):
        """ show tool tip """
        if not self.isEnter:
            return

        self._tooltip.setText(self.toolTip())
        self._tooltip.adjustPos(self.mapToGlobal(QPoint()), self.size())
        self._tooltip.show()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.isEnter = False
        if self._tooltip:
            self._tooltip.hide()

    def hideEvent(self, e):
        super().hideEvent(e)
        if self._tooltip:
            self._tooltip.hide()

    def setDarkToolTip(self, dark=False):
        """ set whether to use the dark theme of tooltip """
        self._isDarkTheme = dark

    def setToolTipDelay(self, delay: int):
        """ set the delay of tool tip """
        self._tooltipDelay = delay

    def hideToolTip(self):
        """ hide tooltip """
        if self._tooltip:
            self._tooltip.hide()
