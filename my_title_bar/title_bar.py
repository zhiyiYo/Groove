import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget

from .title_bar_buttons import (CloseButton, MaximizeButton, MinimizeButton,
                                ReturnButton)


class TitleBar(QWidget):
    """ 定义标题栏 """

    def __init__(self, parent):
        super().__init__(parent)
        self.resize(1360, 40)
        self.win = parent

        # 实例化小部件
        self.title = QLabel('Groove 音乐',self)
        self.minBt = MinimizeButton(self)
        self.maxBt = MaximizeButton(self)
        self.closeBt = CloseButton(self)
        self.returnButton = ReturnButton(self)
        # 记录鼠标按下的位置
        self.startPos = None

        self.initWidget()
        self.adjustButtonPos()

    def initWidget(self):
        """ 初始化小部件 """
        self.isPressed = False
        self.setFixedHeight(40)
        self.setStyleSheet("QWidget{background-color:transparent}\
                            QLabel{font:14px 'Microsoft YaHei Light'; padding:10px 15px 10px 15px;}")
        # 隐藏抬头
        self.title.hide()
        # 将按钮的点击信号连接到槽函数
        self.minBt.clicked.connect(self.win.showMinimized)
        self.maxBt.clicked.connect(self.showRestoreWindow)
        self.closeBt.clicked.connect(self.win.deleteLater)

    def adjustButtonPos(self):
        """ 初始化小部件位置 """
        self.title.move(self.returnButton.width(),0)
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
        if self.win.isMaximized():
            self.win.resize(QApplication.desktop().width(),
                            QApplication.desktop().height() - 50)
        if self.startPos:
            movePos = event.globalPos() - self.startPos
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
