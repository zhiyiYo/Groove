import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt,QAbstractAnimation,QPropertyAnimation
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QToolButton
sys.path.append('..')
from Groove.my_widget.my_button import NavigationButton
from effects.window_effect import WindowEffect


class NavigationMenu(QWidget):
    """ 侧边导航菜单 """
    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建按钮
        self.createButtons()
        # 创建布局
        self.h_layout = QHBoxLayout()
        self.all_v_layout = QVBoxLayout(self)
        # 实例化窗口特效
        self.windowEffect = WindowEffect()
        
        # 初始化界面
        
    
    def createButtons(self):
        """实例化按钮 """
        self.showMenuButton = NavigationButton(
            r'resource\images\navigationBar\黑色最大化导航栏.png', parent=self)
        self.musicGroupButton = NavigationButton(
            r'resource\images\navigationBar\黑色我的音乐.png', '我的音乐', self, (60, 62))
        self.historyButton = NavigationButton(
            r'resource\images\navigationBar\黑色最近播放.png','最近播放的内容', self, (60, 62))
        self.playingButton = NavigationButton(
            r'resource\images\navigationBar\黑色导航栏正在播放.png','正在播放',self,(60, 62))
        self.playListButton = NavigationButton(
            r'resource\images\navigationBar\黑色播放列表.png', '播放列表', self)
        self.createListButton = NavigationButton(
            r'resource\images\navigationBar\黑色新建播放列表.png', parent=self)
        self.settingButton = NavigationButton(
            r'resource\images\navigationBar\黑色设置按钮.png', '设置', self)
        self.myLoveButton = NavigationButton(
            r'resource\images\navigationBar\黑色我喜欢_60_62.png', '我喜欢', self)
        # 创建一个按钮列表
        self.button_list = [self.showMenuButton, self.musicGroupButton,
                            self.historyButton, self.playingButton, self.playListButton,
                            self.createListButton, self.myLoveButton, self.settingButton]
                            
    def initWidget(self):
        """ 初始化小部件 """
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.hWnd=HWND(int(self.winId()))
        self.windowEffect.setAcrylicEffect(self.hWnd,'F2F2F210')

    
