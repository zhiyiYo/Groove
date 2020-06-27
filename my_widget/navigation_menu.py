import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt,QAbstractAnimation,QPropertyAnimation
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QToolButton,QLabel
sys.path.append('..')
from Groove.my_widget.my_button import NavigationButton
from Groove.effects.window_effect import WindowEffect
from Groove.my_widget.my_lineEdit import SearchLineEdit


class NavigationMenu(QWidget):
    """ 侧边导航菜单 """
    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建标题和搜索框
        self.titleLabel = QLabel('Groove音乐')
        self.searchLineEdit = SearchLineEdit(self)
        # 创建按钮
        self.createButtons()
        # 创建布局
        self.h_layout = QHBoxLayout()
        self.all_v_layout = QVBoxLayout()
        # 实例化窗口特效
        self.windowEffect = WindowEffect()
        
        # 初始化界面
        self.initWidget()
        self.initLayout()
        self.setQss()
    
    def createButtons(self):
        """实例化按钮 """
        self.showMenuButton = NavigationButton(
            r'resource\images\navigationBar\黑色最大化导航栏.png', parent=self)
        self.musicGroupButton = NavigationButton(
            r'resource\images\navigationBar\黑色我的音乐.png', '我的音乐', self, (400,60), (60, 62))
        self.historyButton = NavigationButton(
            r'resource\images\navigationBar\黑色最近播放.png','最近播放的内容', self, (400,62), (60, 62))
        self.playingButton = NavigationButton(
            r'resource\images\navigationBar\黑色导航栏正在播放.png', '正在播放', self, (400, 62), (60, 62))
        self.playListButton = NavigationButton(
            r'resource\images\navigationBar\黑色播放列表.png', '播放列表', self, (340,60))
        self.createListButton = NavigationButton(
            r'resource\images\navigationBar\黑色新建播放列表.png', parent=self)
        self.myLoveButton = NavigationButton(
            r'resource\images\navigationBar\黑色我喜欢_60_62.png', '我喜欢', self, (400, 62), (60, 62))
        self.settingButton = NavigationButton(
            r'resource\images\navigationBar\黑色设置按钮.png', '设置', self, (400, 62), (60, 62))
        # 创建一个小部件列表
        self.widget_list = [self.titleLabel, self.showMenuButton, self.searchLineEdit,
                            self.musicGroupButton, self.historyButton, self.playingButton,
                            self.playListButton,self.createListButton, self.myLoveButton, self.settingButton]
                            
    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(400)
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName('navigationMenu')
        # 开启亚克力效果
        self.hWnd = HWND(int(self.winId()))
        self.windowEffect.setAcrylicEffect(self.hWnd, 'F2F2F23F')
        # 设置小部件尺寸
        self.titleLabel.setFixedHeight(60)
        self.playListButton.setFixedWidth(340)

    def initLayout(self):
        """ 初始化布局 """
        self.h_layout.setSpacing(0)
        self.all_v_layout.setSpacing(0)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.all_v_layout.setContentsMargins(0, 0, 0, 0)
        # 将小部件添加到布局中
        for widget in self.widget_list[:7]:
            self.all_v_layout.addWidget(widget)
        self.h_layout.addWidget(self.playListButton)
        self.h_layout.addWidget(self.createListButton,0,Qt.AlignRight)
        self.all_v_layout.addLayout(self.h_layout)
        self.all_v_layout.addWidget(self.myLoveButton)
        self.all_v_layout.addWidget(self.settingButton, 0, Qt.AlignBottom)
        self.all_v_layout.addSpacing(123)
        # 设置总布局
        self.setLayout(self.all_v_layout)
        
    def setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\navigationBar.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = NavigationMenu()
    demo.show()
    sys.exit(app.exec_())


    
