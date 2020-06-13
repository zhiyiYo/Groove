import sys
from ctypes import cdll
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QApplication, QWidget,QPushButton,QLabel


class Demo(QWidget):
    """ 磨砂效果的实现 """

    def __init__(self):
        super().__init__()
        #self.move(800,300)
        self.resize(500, 500)
        #去除边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        #背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        #设置背景色
        self.bgColor = QColor(255, 50, 50, 80)

        # 实例化小部件
        self.label=QLabel('测试',self)
        
        
        # 调用api
        hWnd = HWND(int(self.winId()))   # 不能直接HWND(self.winId()),不然会报错
        cdll.LoadLibrary('Aero\\aeroDll.dll').setBlur(hWnd)
        print(f'主窗口的句柄：{hWnd}')
        #self.bt = AeroButton('AERO',self)
        #初始化小部件
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.label.move(240, 240)
        #self.bt.move(220,235)

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bgColor)
        painter.drawRoundedRect(self.rect(), 20, 20)


class AeroButton(QPushButton):
    """ 磨砂按钮 """
    def __init__(self, text=None, parent=None):
        super().__init__(text, parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.bgColor = QColor(50,50,150,80)
        # 调用api
        hWnd = HWND(int(self.winId()))  # 不能直接HWND(self.winId()),不然会报错
        cdll.LoadLibrary('Aero\\aeroDll.dll').setBlur(hWnd)
        print(f'按钮的句柄：{hWnd}')

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bgColor)
        painter.drawRoundedRect(self.rect(), 20, 20)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    bt=AeroButton()
    demo.show()
    bt.show()
    
    sys.exit(app.exec_())
