import sys

from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QEnterEvent, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton


class ReturnButton(QPushButton):
    """ 返回按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(57, 40)
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(QIcon('resource\\images\\titleBar\\黑色返回按钮_60_40.png'))
        self.setIconSize(QSize(60, 40))
        self.installEventFilter(self)

    def eventFilter(self, obj, e: QEvent):
        """ hover或leave时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.setIcon(
                    QIcon('resource\\images\\titleBar\\黑色返回按钮_hover_60_40.png'))
            elif e.type() == QEvent.Leave:
                self.setIcon(
                    QIcon('resource\\images\\titleBar\\黑色返回按钮_60_40.png'))
            elif e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
                self.setIcon(
                    QIcon(r"resource\images\titleBar\黑色返回按钮_selected_60_40.png"))
        return super().eventFilter(obj, e)


class MinimizeButton(QPushButton):
    """ 定义最小化按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(57, 40)
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(QIcon('resource\\images\\titleBar\\透明黑色最小化按钮_57_40.png'))
        self.setIconSize(QSize(57, 40))
        self.installEventFilter(self)

    def eventFilter(self, obj, e:QEvent):
        """ hover或leave时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.setIcon(
                    QIcon('resource\\images\\titleBar\\绿色最小化按钮_hover_57_40.png'))
            elif e.type() == QEvent.Leave:
                self.setIcon(
                    QIcon('resource\\images\\titleBar\\透明黑色最小化按钮_57_40.png'))
            elif e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
                self.setIcon(
                    QIcon(r"resource\images\titleBar\黑色最小化按钮_selected_57_40.png"))
        return super().eventFilter(obj, e)


class MaximizeButton(QPushButton):
    """ 定义最大化按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(57, 40)
        # 设置最大化标志位
        self.isMax = False
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(QIcon('resource\\images\\titleBar\\透明黑色最大化按钮_57_40.png'))
        self.setIconSize(QSize(57, 40))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ hover或leave时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                if not self.isMax:
                    self.setIcon(
                        QIcon('resource\\images\\titleBar\\绿色最大化按钮_hover_57_40.png'))
                else:
                    self.setIcon(
                        QIcon('resource\\images\\titleBar\\绿色向下还原按钮_hover_57_40.png'))
            elif e.type() == QEvent.Leave:
                if not self.isMax:
                    self.setIcon(
                        QIcon('resource\\images\\titleBar\\透明黑色最大化按钮_57_40.png'))
                else:
                    self.setIcon(
                        QIcon('resource\\images\\titleBar\\黑色向下还原按钮_57_40.png'))
            elif e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
                if not self.isMax:
                    self.setIcon(
                        QIcon(r"resource\images\titleBar\黑色最大化按钮_selected_57_40.png"))
                else:
                    self.setIcon(
                        QIcon(r"resource\images\titleBar\向下还原按钮_selected_57_40.png"))
        return super().eventFilter(obj, e)


class CloseButton(QPushButton):
    """ 定义关闭按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(57, 40)
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(QIcon('resource\\images\\titleBar\\透明黑色关闭按钮_57_40.png'))
        self.setIconSize(QSize(57, 40))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ hover或leave时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.setIcon(
                    QIcon('resource\\images\\titleBar\\关闭按钮_hover_57_40.png'))
            elif e.type() == QEvent.Leave:
                self.setIcon(
                    QIcon('resource\\images\\titleBar\\透明黑色关闭按钮_57_40.png'))
            elif e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
                self.setIcon(
                    QIcon(r"resource\images\titleBar\关闭按钮_selected_57_40.png"))
        return super().eventFilter(obj, e)
        
