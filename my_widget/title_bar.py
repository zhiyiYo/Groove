import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent, QIcon
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QSizePolicy,
                             QSpacerItem, QWidget)

from .my_button import CloseButton, MaximizeButton, MinimizeButton


class TitleBar(QWidget):
    """ 定义标题栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(1360, 40)
        self.win = parent

        # 实例化按钮
        self.minBt = MinimizeButton(self)
        self.maxBt = MaximizeButton(self)
        self.closeBt = CloseButton(self)

        self.initWidget()
        self.adjustButtonPos()

    def initWidget(self):
        """ 初始化小部件 """
        self.isPressed = False
        self.setFixedHeight(40)
        self.setStyleSheet("background-color:transparent")

        # 将按钮的点击信号连接到槽函数
        self.minBt.clicked.connect(self.win.showMinimized)
        self.maxBt.clicked.connect(self.showRestoreWindow)
        self.closeBt.clicked.connect(self.win.close)

    def adjustButtonPos(self):
        """ 初始化小部件位置 """
        self.closeBt.move(self.width() - 57, 0)
        self.maxBt.move(self.width() - 2 * 57, 0)
        self.minBt.move(self.width()-3*57, 0)

    def resizeEvent(self, e: QResizeEvent):
        """ 尺寸改变时移动按钮 """
        self.adjustButtonPos()

    def mouseDoubleClickEvent(self, event):
        """ 双击最大化窗口 """
        self.showRestoreWindow()

    def mousePressEvent(self, event):
        self.isPressed = True
        self.startPos = event.globalPos()  # 记录鼠标点击的位置

    def mouseReleaseEvent(self, event):
        self.isPressed = False

    def mouseMoveEvent(self, event):
        if self.isPressed:
            if self.win.isMaximized:
                self.win.showNormal()

                # 计算窗口应该移动的距离
            movePos = event.globalPos() - self.startPos
            self.startPos = event.globalPos()
            self.win.move(self.win.pos() + movePos)

    def showRestoreWindow(self):
        """ 复原窗口并更换最大化按钮的图标 """
        if self.win.isMaximized():
            self.win.showNormal()
            self.maxBt.isMax = False
            self.maxBt.setIcon(
                QIcon('resource\\images\\titleBar\\黑色最大化按钮_57_40.png'))
        else:
            self.win.showMaximized()
            self.maxBt.isMax = True
            self.maxBt.setIcon(
                QIcon('resource\\images\\titleBar\\黑色向下还原按钮_57_40.png'))


class Demo(QWidget):
    """ 测试标题栏 """

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color:white")
        self.titleBar = TitleBar(self)

    def resizeEvent(self, e):
        self.titleBar.move(self.width()-self.titleBar.width(), 0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
