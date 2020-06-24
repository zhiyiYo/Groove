import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget,QSlider,QHBoxLayout,QLineEdit

sys.path.append('..')
from Groove.effects.window_effect import WindowEffect


class PlayBar(QWidget):
    """ 底部播放栏 """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 实例化窗口特效
        self.windowEffect = WindowEffect()
        self.hWnd = HWND(int(self.winId()))

        # 实例化小部件
        self.h_layout = QHBoxLayout()
        self.alphaValue = QLineEdit('66', self)
        self.alphaSlider = QSlider(Qt.Horizontal,self)
        
        
        # 初始化小部件
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        """ 初始化小部件 """
        #self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(113)
        self.resize(400,113)
        self.setStyleSheet('background:transparent')
        self.alphaValue.setStyleSheet('background:white;width:30px')
        self.alphaSlider.setStyleSheet('background:transparent')
        
        
        self.windowEffect.setAcrylicEffect(self.hWnd, 'FF000066')
        self.alphaValue.textChanged.connect(
            lambda: self.setAcrylicColor('FF0000'+self.alphaValue.text()))
        
    def initLayout(self):
        """ 初始化布局 """
        self.h_layout.addWidget(self.alphaSlider,0, Qt.AlignCenter)
        self.h_layout.addWidget(self.alphaValue, 0, Qt.AlignCenter)
        self.setLayout(self.h_layout)

    def setAcrylicColor(self,gradientColor:str):
        """ 设置亚克力效果的混合色 """
        self.windowEffect.setAcrylicEffect(self.hWnd, gradientColor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = PlayBar()
    demo.show()
    sys.exit(app.exec_())
