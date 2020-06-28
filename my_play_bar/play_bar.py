import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget,QSlider,QHBoxLayout,QLineEdit,QVBoxLayout

sys.path.append('..')
from Groove.effects.window_effect import WindowEffect
from Groove.my_play_bar.play_progress_bar import PlayProgressBar
from Groove.my_play_bar.central_button_group import CentralButtonGroup
from Groove.my_play_bar.right_widget_group import RightWidgetGroup


class PlayBar(QWidget):
    """ 底部播放栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 实例化窗口特效
        self.windowEffect = WindowEffect()
        self.hWnd = HWND(int(self.winId()))

        # 实例化小部件
        self.playProgressBar = PlayProgressBar(self)
        self.centralButtonGroup = CentralButtonGroup(self)
        self.rightWidgetGroup = RightWidgetGroup(self)
        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.all_v_layout = QVBoxLayout(self)
        
        # 初始化小部件
        self.initWidget()
        self.initLayout()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setFixedHeight(113)
        self.resize(1180,113)
        # 设置亚克力背景色
        self.setAcrylicColor('7d83918F')
        
    def initLayout(self):
        """ 初始化布局 """
        self.all_v_layout.setSpacing(0)
        self.all_v_layout.setContentsMargins(0, 0, 0, 0)
        self.all_v_layout.addWidget(self.centralButtonGroup, 0, Qt.AlignCenter)
        self.all_v_layout.addWidget(self.playProgressBar, 0, Qt.AlignCenter)
        self.rightWidgetGroup.move(self.width()-self.rightWidgetGroup.width(),0)

    def setAcrylicColor(self,gradientColor:str):
        """ 设置亚克力效果的混合色 """
        self.windowEffect.setAcrylicEffect(self.hWnd, gradientColor)

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\playBar.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        self.rightWidgetGroup.move(
            self.width()-self.rightWidgetGroup.width(), 0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = PlayBar()
    demo.show()
    sys.exit(app.exec_())
