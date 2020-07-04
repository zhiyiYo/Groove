import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QToolButton
sys.path.append('..')
from Groove.navigation.navigation_button import ToolButton


class NavigationBar(QWidget):
    """ 侧边导航栏 """
    def __init__(self, parent,navigationMenu=None):
        super().__init__(parent)
        # 引用配置文件数据并设置绑定菜单
        self.config = self.parent().settingInterface.config
        self.navigationMenu = navigationMenu
        # 实例化按钮
        self.createButtons()
        # 实例化垂直布局
        self.v_layout = QVBoxLayout()
        # 初始化界面
        self.initWidget()
        self.initLayout()
        self.setQss()
        
    def createButtons(self):
        """实例化按钮 """
        self.showMenuButton = ToolButton(
            r'resource\images\navigationBar\黑色最大化导航栏.png', parent=self)
        self.searchButton = ToolButton(
            r'resource\images\navigationBar\黑色搜索.png', parent=self, buttonSize=(60, 62))
        self.musicGroupButton = ToolButton(
            r'resource\images\navigationBar\黑色我的音乐.png', parent=self, buttonSize=(60, 62))
        self.historyButton = ToolButton(
            r'resource\images\navigationBar\黑色最近播放.png', parent=self, buttonSize=(60, 62))
        self.playingButton = ToolButton(
            r'resource\images\navigationBar\黑色导航栏正在播放.png', parent=self, buttonSize=(60, 62))
        self.playListButton = ToolButton(
            r'resource\images\navigationBar\黑色播放列表.png', parent=self)
        self.createPlayListButton = ToolButton(
            r'resource\images\navigationBar\黑色新建播放列表.png', parent=self)
        self.settingButton = ToolButton(
            r'resource\images\navigationBar\黑色设置按钮.png', parent=self)
        # 创建一个按钮列表
        self.button_list = [self.showMenuButton, self.searchButton, self.musicGroupButton,
                            self.historyButton, self.playingButton, self.playListButton,
                            self.createPlayListButton, self.settingButton]
        # 可变样式的按钮列表
        self.updatableButton_list = self.button_list[2:6] + [self.settingButton]
                            
    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(60)
        self.setObjectName('navigationBar')  
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)    
        # 将部分按钮的点击信号连接到槽函数并设置属性
        name_list = ['musicGroupButton', 'historyButton',
                     'playingButton', 'playListButton', 'settingButton']
        for button,name in zip(self.updatableButton_list,name_list):
            button.clicked.connect(self.buttonClickedEvent)
            button.setProperty('name',name)
        
    def initLayout(self):
        """ 初始化布局 """
        # 留出标题栏返回键的位置
        self.v_layout.addSpacing(40)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0,0,0,0)
        for button in self.button_list[:-1]:
            self.v_layout.addWidget(button)
        self.v_layout.addWidget(self.settingButton, 0, Qt.AlignBottom)
        # 留出底部播放栏的位置
        self.v_layout.addSpacing(123)
        self.setLayout(self.v_layout)

    def buttonClickedEvent(self):
        """ 按钮点击时更新样式并更换界面 """
        for button in self.updatableButton_list:
            if self.sender() == button:
                button.isSelected=True
            else:
                button.isSelected=False
        # 更新按钮的样式
        for button in self.button_list:
            button.update()
        if self.navigationMenu:
            for button in self.navigationMenu.updatableButton_list:
                if button.property('name') == self.sender().property('name'):
                    button.isSelected = True
                else:
                    button.isSelected = False
            for button in self.navigationMenu.updatableButton_list:
                button.update()
        # 切换界面
        if self.sender() == self.musicGroupButton:
            # 更新配置文件的下标
            self.config['current-index'] = 0
            self.config['pre-index'] = self.parent().stackedWidget.currentIndex()
            self.parent().stackedWidget.setCurrentWidget(self.parent().myMusicInterface)
        elif self.sender() == self.settingButton:
            self.config['current-index'] = 1
            self.config['pre-index'] = self.parent().stackedWidget.currentIndex()
            self.parent().stackedWidget.setCurrentWidget(self.parent().settingInterface)

    def setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\navigation.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def setBoundNavigationMenu(self, navigationMenu):
        """ 设置绑定导航菜单 """
        self.navigationMenu = navigationMenu

