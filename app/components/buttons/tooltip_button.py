# coding:utf-8
from components.widgets.tooltip import Tooltip
from PyQt5.QtCore import QEvent, QObject, QPoint
from PyQt5.QtWidgets import QApplication, QToolButton, QPushButton


class TooltipButton(QToolButton):
    """ 带工具提示的工具按钮 """

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

        # 更新工具提示
        if self.__tooltip.text != self.toolTip():
            self.__tooltip.setText(self.toolTip())

        # 必须将工具提示移动到按钮区域之外
        pos = self.mapTo(self.window(), QPoint(0, 0))
        x = pos.x() + self.width()//2 - self.__tooltip.width()//2
        y = pos.y() - 2 - self.__tooltip.height()

        # 调整坐标，防止工具提示出现在界面以外
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
        """ 设置工具提示的主题 """
        self.__darkTooltip = dark

    def hideToolTip(self):
        """ 隐藏工具提示 """
        if self.__tooltip:
            self.__tooltip.hide()


class TooltipPushButton(QPushButton):
    """ 带工具提示的 Push 按钮 """

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

        # 更新工具提示
        if self.__tooltip.text != self.toolTip():
            self.__tooltip.setText(self.toolTip())

        # 必须将工具提示移动到按钮区域之外
        pos = self.mapTo(self.window(), QPoint(0, 0))
        x = pos.x() + self.width()//2 - self.__tooltip.width()//2
        y = pos.y() - 2 - self.__tooltip.height()

        # 调整坐标，防止工具提示出现在界面以外
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
        """ 设置工具提示的主题 """
        self.__darkTooltip = dark

    def hideToolTip(self):
        """ 隐藏工具提示 """
        if self.__tooltip:
            self.__tooltip.hide()
