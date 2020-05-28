# coding:utf-8

""" 自定义按钮库"""

import sys

from PyQt5.QtCore import Qt, QEvent, QPoint, QTimer,QSize
from PyQt5.QtGui import QBitmap, QPainter, QPixmap, QBrush, QEnterEvent, QIcon
from PyQt5.QtWidgets import QApplication, QPushButton, QToolTip


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
        self.setToolTip('全部播放')

        # 设置背景图
        self.image = QPixmap('resource\\images\\歌手播放按钮_67_67.png')

        # 设置监听
        self.installEventFilter(self)

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

    def eventFilter(self, obj, e):
        """ hover时变大,没有hover时变小 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.enter = True
                self.update()
            elif e.type() == QEvent.Leave:
                self.enter = False
                self.update()
        return False


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

        # 设置背景图
        self.image = QPixmap('resource\\images\\歌手添加到按钮_65_65.png')

        # 设置悬浮提示
        self.setToolTip('添加到')

        # 设置监听
        self.installEventFilter(self)

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

    def eventFilter(self, obj, e):
        """ hover时变大,没有hover时变小 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.enter = True
                self.update()

            elif e.type() == QEvent.Leave:
                self.enter = False
                self.update()
        return False


class BlackMinimizeButton(QPushButton):
    """ 定义黑底的最小化按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(57, 40)
        # 扁平化
        self.setFlat(True)
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(QIcon('resource\\images\\最小化按钮_57_40.png'))
        self.setIconSize(QSize(57, 40))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ hover或leave时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.setIcon(QIcon('resource\\images\\最小化按钮_hover_57_40.png'))
            elif e.type() == QEvent.Leave:
                self.setIcon(QIcon('resource\\images\\最小化按钮_57_40.png'))
        return False


class BlackMaximizeButton(QPushButton):
    """ 定义黑底的最大化按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(57, 40)
        # 扁平化
        self.setFlat(True)
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(QIcon('resource\\images\\最大化按钮_57_40.png'))
        self.setIconSize(QSize(57, 40))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ hover或leave时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.setIcon(QIcon('resource\\images\\最大化按钮_hover_57_40.png'))
            elif e.type() == QEvent.Leave:
                self.setIcon(QIcon('resource\\images\\最大化按钮_57_40.png'))
        return False


class BlackCloseButton(QPushButton):
    """ 定义黑底的关闭按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(57, 40)
        # 扁平化
        #self.setFlat(True)
        self.setStyleSheet("QPushButton{border:none;margin:0}")
        self.setIcon(QIcon('resource\\images\\关闭按钮_57_40.png'))
        self.setIconSize(QSize(57, 40))
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ hover或leave时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.setIcon(QIcon('resource\\images\\关闭按钮_hover_57_40.png'))
            elif e.type() == QEvent.Leave:
                self.setIcon(QIcon('resource\\images\\关闭按钮_57_40.png'))
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongerPlayButton()
    demo.show()
    sys.exit(app.exec_())
