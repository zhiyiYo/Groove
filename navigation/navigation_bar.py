import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QToolButton, QVBoxLayout, QWidget

from my_create_playlist_interface.create_playlist_button import \
    CreatePlaylistButton
from my_widget.button_group import ButtonGroup
from navigation.navigation_button import ToolButton


class NavigationBar(QWidget):
    """ 侧边导航栏 """
    def __init__(self, parent=None, navigationMenu=None):
        super().__init__(parent)
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
            r'resource\images\navigationBar\黑色搜索.png',
            parent=self,
            buttonSize=(60, 62))
        self.musicGroupButton = ToolButton(
            r'resource\images\navigationBar\黑色我的音乐.png',
            parent=self,
            buttonSize=(60, 62))
        self.historyButton = ToolButton(
            r'resource\images\navigationBar\黑色最近播放.png',
            parent=self,
            buttonSize=(60, 62))
        self.playingButton = ToolButton(
            r'resource\images\navigationBar\黑色导航栏正在播放.png',
            parent=self,
            buttonSize=(60, 62))
        self.playListButton = ToolButton(
            r'resource\images\navigationBar\黑色播放列表.png', parent=self)
        self.createPlaylistButton = CreatePlaylistButton(self)
        self.settingButton = ToolButton(
            r'resource\images\navigationBar\黑色设置按钮.png', parent=self)
        # 创建一个按钮列表
        self.button_list = [
            self.showMenuButton, self.searchButton, self.musicGroupButton,
            self.historyButton, self.playingButton, self.playListButton,
            self.createPlaylistButton, self.settingButton
        ]
        # 可变样式的按钮列表
        self.updatableButton_list = self.button_list[2:6] + [self.settingButton]
        self.currentButton = self.musicGroupButton

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(60)
        self.setObjectName('navigationBar')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 将部分按钮的点击信号连接到槽函数并设置属性
        self.__buttonName_list = [
            'musicGroupButton', 'historyButton', 'playingButton',
            'playListButton', 'settingButton'
        ]
        for button, name in zip(self.updatableButton_list, self.__buttonName_list):
            button.setProperty('name', name)
        self.musicGroupButton.clicked.connect(
            lambda: self.setSelectedButton('musicGroupButton'))
        self.historyButton.clicked.connect(
            lambda: self.setSelectedButton('historyButton'))
        self.playingButton.clicked.connect(
            lambda: self.setSelectedButton('playingButton'))
        self.playListButton.clicked.connect(
            lambda: self.setSelectedButton('playListButton'))
        self.settingButton.clicked.connect(
            lambda: self.setSelectedButton('settingButton'))

    def initLayout(self):
        """ 初始化布局 """
        # 留出标题栏返回键的位置
        self.v_layout.addSpacing(40)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        for button in self.button_list[:-1]:
            self.v_layout.addWidget(button)
        self.v_layout.addWidget(self.settingButton, 0, Qt.AlignBottom)
        # 留出底部播放栏的位置
        self.v_layout.addSpacing(123)
        self.setLayout(self.v_layout)

    def setSelectedButton(self, selectedButtonName,isSendBySelf=True):
        """ 设置选中的按钮 """
        if selectedButtonName == 'playingButton':
            return
        self.currentButton.setSelected(False)
        if selectedButtonName in self.__buttonName_list:
            self.currentButton = self.updatableButton_list[self.__buttonName_list.index(
                selectedButtonName)]
            self.currentButton.setSelected(True)
        # 更新绑定的任务栏的按钮的标志位和样式
        if self.navigationMenu and isSendBySelf:
            self.navigationMenu.setSelectedButton(selectedButtonName,False)

    def setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\navigation.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def setBoundNavigationMenu(self, navigationMenu):
        """ 设置绑定导航菜单 """
        self.navigationMenu = navigationMenu
