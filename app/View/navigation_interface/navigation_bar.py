# coding:utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout

from .basic_navigation_widget import BasicNavigationWidget
from .navigation_button import CreatePlaylistButton, ToolButton


class NavigationBar(BasicNavigationWidget):
    """ 侧边导航栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 实例化按钮
        self.__createButtons()
        # 实例化垂直布局
        self.v_layout = QVBoxLayout()
        # 初始化界面
        self.__initWidget()

    def __createButtons(self):
        """实例化按钮 """
        self.showMenuButton = ToolButton(
            r'app\resource\images\navigation_interface\GlobalNavButton.png', parent=self)
        self.searchButton = ToolButton(
            r'app\resource\images\navigation_interface\Search.png', (60, 62), self)
        self.musicGroupButton = ToolButton(
            r'app\resource\images\navigation_interface\MusicInCollection.png', (60, 62), self)
        self.historyButton = ToolButton(
            r'app\resource\images\navigation_interface\Recent.png', (60, 62), self)
        self.playingButton = ToolButton(
            r'app\resource\images\navigation_interface\黑色导航栏正在播放.png', (60, 62), self)
        self.playlistButton = ToolButton(
            r'app\resource\images\navigation_interface\黑色播放列表.png', parent=self)
        self.createPlaylistButton = CreatePlaylistButton(self)
        self.settingButton = ToolButton(
            r'app\resource\images\navigation_interface\Settings.png', parent=self)
        # 初始化当前选中的按钮
        self.currentButton = self.musicGroupButton
        # 创建一个按钮列表
        self.button_list = [
            self.showMenuButton, self.searchButton, self.musicGroupButton,
            self.historyButton, self.playingButton, self.playlistButton,
            self.createPlaylistButton, self.settingButton
        ]
        # 可变样式的按钮列表
        self._selectableButtons = self.button_list[2:6] + [
            self.settingButton]
        # 创建按钮与下标对应的字典
        self._selectableButtonNames = [
            'musicGroupButton', 'historyButton', 'playingButton',
            'playlistButton', 'settingButton'
        ]

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(60)
        self.setSelectedButton(self.musicGroupButton.property('name'))
        # 将部分按钮的点击信号连接到槽函数并设置属性
        self._connectButtonClickedSigToSlot()
        # 初始化布局
        self.__initLayout()

    def __initLayout(self):
        """ 初始化布局 """
        # 留出标题栏返回键的位置
        self.v_layout.addSpacing(40)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        for button in self.button_list[:-1]:
            self.v_layout.addWidget(button)
        self.v_layout.addWidget(self.settingButton, 0, Qt.AlignBottom)
        # 留出底部播放栏的位置
        self.v_layout.addSpacing(127)
        self.setLayout(self.v_layout)
