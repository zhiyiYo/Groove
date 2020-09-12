# coding:utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from .play_bar_buttons import VolumeButton, BasicButton

from my_widget.my_slider import Slider


class RightWidgetGroup(QWidget):
    """ 播放按钮组 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建小部件
        self.volumeButton = VolumeButton(self)
        self.volumeSlider = Slider(Qt.Horizontal, self)
        self.smallPlayModeButton = BasicButton(
            r'resource\images\playBar\最小播放模式_45_45.png', self)
        self.moreActionsButton = BasicButton(
            r'resource\images\playBar\更多操作_45_45.png',self)
        self.widget_list = [self.volumeButton, self.volumeSlider,
                            self.smallPlayModeButton, self.moreActionsButton]
        # 创建布局
        self.h_layout = QHBoxLayout()
        # 初始化界面
        self.__initWidget()
        self.__initLayout()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(301, 16 + 67)
        self.volumeSlider.setRange(0,100)
        self.volumeSlider.setObjectName('volumeSlider')
        # 将音量滑动条数值改变信号连接到槽函数
        self.volumeSlider.setValue(20)
                            
    def __initLayout(self):
        """ 初始化布局 """
        self.__spacing_list = [7, 8, 8, 5, 7]
        self.h_layout.setSpacing(0)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        # 将小部件添加到布局中
        for i in range(4):
            self.h_layout.addSpacing(self.__spacing_list[i])
            self.h_layout.addWidget(self.widget_list[i])
        else:
            self.h_layout.addSpacing(self.__spacing_list[-1])
        self.setLayout(self.h_layout)

