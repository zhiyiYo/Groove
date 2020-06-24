# coding:utf-8

""" 自定义按钮库"""

import sys

from PyQt5.QtCore import QEvent, QPoint, QSize, Qt, QTimer
from PyQt5.QtGui import QBrush, QEnterEvent, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import (QApplication, QGraphicsBlurEffect, QLabel,
                             QPushButton, QToolButton)


class SongerPlayButton(QPushButton):
    """ 歌手头像上的播放按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(67, 67)

        # 隐藏边框并将背景设置为透明
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置鼠标进入标志位
        self.enter = False
        # 设置悬浮提醒
        self.customToolTip = None

        # 设置背景图
        self.image = QPixmap('resource\\images\\歌手播放按钮_67_67.png')

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        # 设置背景图
        brush = QBrush(self.image)
        painter.setBrush(brush)
        # 绘制背景图
        if not self.enter:
            painter.drawEllipse(5, 5, 57, 57)
        else:
            painter.drawEllipse(0, 0, 67, 67)

    def setCustomToolTip(self, toolTip, toolTipText: str):
        """ 设置提示条和提示条的位置 """
        self.customToolTip = toolTip
        self.customToolTipText = toolTipText

    def enterEvent(self, e:QEnterEvent):
        """ 鼠标进入按钮时增大按钮并显示提示条 """
        self.enter = True
        self.update()
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            self.customToolTip.move(e.globalX() - int(self.customToolTip.width() / 2), e.globalY() - 100)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 鼠标离开按钮时减小按钮并隐藏提示条 """
        self.enter = False
        self.update()
        if self.customToolTip:
            self.customToolTip.hide()


class SongerAddToButton(QPushButton):
    """ 歌手头像上的添加到按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(65, 65)

        # 隐藏边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置鼠标进入标志位
        self.enter = False
        # 设置悬浮提醒
        self.customToolTip = None

        # 设置背景图
        self.image = QPixmap('resource\\images\\歌手添加到按钮_65_65.png')

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        # 设置背景图
        brush = QBrush(self.image)
        painter.setBrush(brush)
        # 绘制背景图
        if not self.enter:
            painter.drawEllipse(4, 4, 57, 57)
        else:
            painter.drawEllipse(0, 0, 65, 65)

    def setCustomToolTip(self, toolTip, toolTipText: str):
        """ 设置提示条和提示条的位置 """
        self.customToolTip = toolTip
        self.customToolTipText = toolTipText

    def enterEvent(self, e):
        """ 鼠标进入按钮时增大按钮并显示提示条 """
        self.enter = True
        self.update()
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            self.customToolTip.move(
                e.globalX() - int(self.customToolTip.width() / 2), e.globalY() - 100)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 鼠标离开按钮时减小按钮并隐藏提示条 """
        self.enter = False
        self.update()
        if self.customToolTip:
            self.customToolTip.hide()


class SongCardPlayButton(QToolButton):
    """ 定义歌曲卡播放按钮 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(61, 61)
        self.setObjectName('playButton')
        self.setIcon(QIcon('resource\\images\\black_play_bt.png'))
        self.setIconSize(QSize(61, 61))
        

class SongCardAddToButton(QToolButton):
    """ 定义歌曲卡添加到按钮 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(61, 61)
        self.setObjectName('addToButton')
        self.setIcon(QIcon('resource\\images\\black_addTo_bt.png'))
        self.setIconSize(QSize(61, 61))


class RandomPlayButton(QPushButton):
    """ 定义条形随机播放按钮 """
    def __init__(self, text='', slot=None, parent=None):
        super().__init__(text, parent)
        self.setIcon(QIcon('resource\\images\\无序播放所有_130_17.png'))
        self.setIconSize(QSize(130, 17))
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName('randomPlayButton')
        self.clicked.connect(slot)
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ 当鼠标移到播放模式按钮上时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter or e.type() == QEvent.HoverMove:
                self.setIcon(QIcon('resource\\images\\无序播放所有_hover_130_17.png'))
            elif e.type() == QEvent.Leave:
                self.setIcon(QIcon('resource\\images\\无序播放所有_130_17.png'))
        return False


class SortModeButton(QPushButton):
    """ 定义排序模式按钮 """
    def __init__(self, text,slot, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName('sortModeButton')
        self.clicked.connect(slot)


class MinimizeButton(QPushButton):
    """ 定义最小化按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(57, 40)
        # 扁平化
        self.setFlat(True)
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(QIcon('resource\\images\\黑色最小化按钮_57_40_2.png'))
        self.setIconSize(QSize(57, 40))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ hover或leave时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.setIcon(QIcon('resource\\images\\最小化按钮_hover_57_40.png'))
            elif e.type() == QEvent.Leave:
                self.setIcon(QIcon('resource\\images\\黑色最小化按钮_57_40_2.png'))
        return False


class MaximizeButton(QPushButton):
    """ 定义最大化按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(57, 40)
        # 设置最大化标志位
        self.isMax = False
        # 扁平化
        self.setFlat(True)
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(QIcon('resource\\images\\黑色最大化按钮_57_40_2.png'))
        self.setIconSize(QSize(57, 40))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ hover或leave时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                if not self.isMax:
                    self.setIcon(
                        QIcon('resource\\images\\最大化按钮_hover_57_40.png'))
                else:
                    self.setIcon(
                        QIcon('resource\\images\\向下还原按钮_hover_57_40.png'))
            elif e.type() == QEvent.Leave:
                if not self.isMax:
                    self.setIcon(
                        QIcon('resource\\images\\黑色最大化按钮_57_40_2.png'))
                else:
                    self.setIcon(QIcon('resource\\images\\黑色向下还原按钮_57_40.png'))
        return False


class CloseButton(QPushButton):
    """ 定义关闭按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(57, 40)
        # 扁平化
        # self.setFlat(True)
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(QIcon('resource\\images\\黑色关闭按钮_57_40_2.png'))
        self.setIconSize(QSize(57, 40))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ hover或leave时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.setIcon(QIcon('resource\\images\\关闭按钮_hover_57_40.png'))
            elif e.type() == QEvent.Leave:
                self.setIcon(QIcon('resource\\images\\黑色关闭按钮_57_40_2.png'))
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongerPlayButton()
    demo.show()
    sys.exit(app.exec_())
