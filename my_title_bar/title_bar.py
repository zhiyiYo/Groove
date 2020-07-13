import sys

from ctypes.wintypes import HWND,MSG

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QResizeEvent,QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget

sys.path.append('..')
from Groove.effects.frameless_window_func import FramelessWindowFunc
from Groove.my_title_bar.title_bar_buttons import (CloseButton, MaximizeButton, MinimizeButton,
                                ReturnButton)

from Groove.flags.wm_hittest import Flags


class TitleBar(QWidget):
    """ 定义标题栏 """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(1360, 40)
        self.win = parent
        # 实例化无边框窗口函数类
        self.framelessWindowFunc = FramelessWindowFunc()
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 实例化小部件
        self.title = QLabel('Groove 音乐',self)
        self.createButtons()
        # 初始化界面
        self.initWidget()
        self.adjustButtonPos()

    def createButtons(self):
        """ 创建各按钮 """
        self.minBt = MinimizeButton(self)
        self.maxBt = MaximizeButton(self)
        self.closeBt = CloseButton(self)
        self.returnBt = ReturnButton(self)
        self.button_list=[self.minBt,self.maxBt,self.closeBt,self.returnBt]

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(40)
        self.setStyleSheet("QWidget{background-color:transparent}\
                            QLabel{font:14px 'Microsoft YaHei Light'; padding:10px 15px 10px 15px;}")
        # 隐藏抬头
        self.title.hide()
        # 将按钮的点击信号连接到槽函数
        self.minBt.clicked.connect(self.win.showMinimized)
        self.maxBt.clicked.connect(self.showRestoreWindow)
        self.closeBt.clicked.connect(self.win.close)

    def adjustButtonPos(self):
        """ 初始化小部件位置 """
        self.title.move(self.returnBt.width(),0)
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
        if self.isPointInDragRegion(event.pos()):
            pass
            self.framelessWindowFunc.moveWindow(HWND(int(self.parent().winId())))


    def showRestoreWindow(self):
        """ 复原窗口并更换最大化按钮的图标 """
        if self.win.isMaximized():
            self.win.showNormal()
            # 更新标志位用于更换图标
            self.maxBt.isMax = False
            self.maxBt.setIcon(
                QIcon('resource\\images\\titleBar\\黑色最大化按钮_57_40.png'))
        else:
            self.win.showMaximized()
            self.maxBt.isMax = True
            self.maxBt.setIcon(
                QIcon('resource\\images\\titleBar\\黑色向下还原按钮_57_40.png'))

    def isPointInDragRegion(self, pos)->bool:
        """ 检查鼠标按下的点是否属于允许拖动的区域 """
        x = pos.x()
        condX = (60 < x < self.width() - 57 * 3)
        return condX


class Demo(QWidget):
    """ 测试标题栏 """

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.titleBar = TitleBar(self)
        self.resize(1200,900)

        
    def resizeEvent(self, e):
        self.titleBar.resize(self.width(), 40)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
