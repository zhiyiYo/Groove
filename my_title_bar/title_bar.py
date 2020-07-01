import sys

from ctypes.wintypes import HWND,MSG,RECT

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget

sys.path.append('..')
from Groove.effects.frameless_window_func import FramelessWindowFunc
from Groove.my_title_bar.title_bar_buttons import (CloseButton, MaximizeButton, MinimizeButton,
                                ReturnButton)


HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17
HTCAPTION = 2

class TitleBar(QWidget):
    """ 定义标题栏 """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(1360, 40)
        self.win = parent
        # 实例化无边框窗口函数类
        self.framelessWindowFunc=FramelessWindowFunc()
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
        # 设置鼠标跟踪
        for bt in self.button_list:
            bt.setMouseTracking(True)

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
        self.setStyleSheet("background-color:white")
        self.titleBar = TitleBar(self)

    def resizeEvent(self, e):
        self.titleBar.resize(self.width(), 0)

    def GET_X_LPARAM(self, param):
        return param & 0xffff

    def GET_Y_LPARAM(self, param):
        return param >> 16
        
    """ def nativeEvent(self, eventType, message):
        result = 0
        msg2 = MSG.from_address(message.__int__())
        #minV, maxV = 18, 22
        minV,maxV=2,6
        if msg2.message == 0x0084:
            xPos = self.GET_X_LPARAM(msg2.lParam) - self.frameGeometry().x()
            yPos = self.GET_Y_LPARAM(msg2.lParam) - self.frameGeometry().y()
#             if self.childAt(xPos,yPos) == 0:
#                 result = HTCAPTION
#             else:
#                 return (False,result)
            if(xPos > minV and xPos < maxV):
                result = HTLEFT
            elif(xPos > (self.width() - maxV) and xPos < (self.width() - minV)):
                result = HTRIGHT
            elif(yPos > minV and yPos < maxV):
                result = HTTOP
            elif(yPos > (self.height() - maxV) and yPos < (self.height() - minV)):
                result = HTBOTTOM
            elif(xPos > minV and xPos < maxV and yPos > minV and yPos < maxV):
                result = HTTOPLEFT
            elif(xPos > (self.width() - maxV) and xPos < (self.width() - minV) and yPos > minV and yPos < maxV):
                result = HTTOPRIGHT
            elif(xPos > minV and xPos < maxV and yPos > (self.height() - maxV) and yPos < (self.height() - minV)):
                result = HTBOTTOMLEFT
            elif(xPos > (self.width() - maxV) and xPos < (self.width() - minV) and yPos > (self.height() - maxV) and yPos < (self.height() - minV)):
                result = HTBOTTOMRIGHT
            else:
                result = HTCAPTION
            return (True, result)
        return  QWidget.nativeEvent(self, eventType, message) """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
