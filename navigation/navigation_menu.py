import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt, QAbstractAnimation, QPropertyAnimation
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QToolButton, QLabel
sys.path.append('..')

from .navigation_button import PushButton,ToolButton
from .search_line_edit import SearchLineEdit
from Groove.my_widget.button_group import ButtonGroup
from Groove.my_create_playlist_interface.create_playlist_button import CreatePlaylistButton


class NavigationMenu(QWidget):
    """ 侧边导航菜单 """
    def __init__(self, navigationBar, parent):
        super().__init__(parent)
        # 引用配置文件数据和导航栏
        self.config = self.parent().settingInterface.config
        self.navigationBar = navigationBar
        # 创建搜索框
        self.searchLineEdit = SearchLineEdit(self)
        # 创建按钮
        self.createButtons()
        # 创建布局
        self.h_layout_1 = QHBoxLayout()
        self.h_layout_2 = QHBoxLayout()
        self.all_v_layout = QVBoxLayout()

        # 初始化界面
        self.initWidget()
        self.initLayout()
        self.setQss()

    def createButtons(self):
        """实例化按钮 """
        # 实例化一个集中管理按钮的类
        self.buttonGroup = ButtonGroup()
        self.showBarButton = ToolButton(
            r'resource\images\navigationBar\黑色最大化导航栏.png', parent=self)
        self.musicGroupButton = PushButton(
            r'resource\images\navigationBar\黑色我的音乐.png', '我的音乐', self,
            (400, 60), (60, 62))
        self.historyButton = PushButton(
            r'resource\images\navigationBar\黑色最近播放.png', '最近播放的内容', self,
            (400, 62), (60, 62))
        self.playingButton = PushButton(
            r'resource\images\navigationBar\黑色导航栏正在播放.png', '正在播放', self,
            (400, 62), (60, 62))
        self.playListButton = PushButton(
            r'resource\images\navigationBar\黑色播放列表.png', '播放列表', self,
            (340, 60))
        self.createPlaylistButton = CreatePlaylistButton(self)
        self.myLoveButton = PushButton(
            r'resource\images\navigationBar\黑色我喜欢_60_62.png', '我喜欢', self,
            (400, 62), (60, 62))
        self.settingButton = PushButton(
            r'resource\images\navigationBar\黑色设置按钮.png', '设置', self, (400, 62),
            (60, 62))
        # 创建一个小部件列表
        self.widget_list = [
            self.showBarButton, self.searchLineEdit, self.musicGroupButton,
            self.historyButton, self.playingButton, self.playListButton,
            self.createPlaylistButton, self.myLoveButton, self.settingButton
        ]
        # 创建要更新样式的按钮列表
        self.updatableButton_list = [
            self.musicGroupButton, self.historyButton, self.playingButton,
            self.playListButton, self.myLoveButton, self.settingButton
        ]
        # 将按钮添加到按钮组中
        self.buttonGroup.addButtons(self.updatableButton_list)

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(400)
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        self.setObjectName('navigationMenu')
        # 将按钮点击信号连接到槽函数并设置属性
        name_list = [
            'musicGroupButton', 'historyButton', 'playingButton',
            'playListButton', 'myLoveButton', 'settingButton'
        ]
        for button, name in zip(self.updatableButton_list, name_list):
            button.setProperty('name', name)
            button.clicked.connect(self.buttonClickedEvent)
        # 分配ID
        self.myLoveButton.setObjectName('myLoveButton')
        self.playListButton.setObjectName('playListButton')

    def initLayout(self):
        """ 初始化布局 """
        # 初始化布局的属性
        self.h_layout_2.setSpacing(0)
        self.all_v_layout.setSpacing(0)
        self.h_layout_1.setContentsMargins(15, 8, 15, 8)
        self.h_layout_2.setContentsMargins(0, 0, 0, 0)
        self.all_v_layout.setContentsMargins(0, 0, 0, 0)
        # 留出标题栏的位置
        self.all_v_layout.addSpacing(40)
        # 将小部件添加到布局中
        self.all_v_layout.addWidget(self.showBarButton)
        self.h_layout_1.addWidget(self.searchLineEdit)
        self.all_v_layout.addLayout(self.h_layout_1)
        for widget in self.widget_list[2:5]:
            self.all_v_layout.addWidget(widget)
        # 添加剩下的按钮
        self.h_layout_2.addWidget(self.playListButton)
        self.h_layout_2.addWidget(self.createPlaylistButton)
        self.all_v_layout.addLayout(self.h_layout_2)
        self.all_v_layout.addWidget(self.myLoveButton)
        self.all_v_layout.addWidget(self.settingButton, 0, Qt.AlignBottom)
        self.all_v_layout.addSpacing(123)
        # 设置总布局
        self.setLayout(self.all_v_layout)

    def buttonClickedEvent(self):
        """ 按钮点击事件 """
        sender = self.sender()
        # 更新自己按钮的标志位和样式
        self.buttonGroup.updateButtons(sender)
        # 更新绑定的任务栏的按钮的标志位和样式
        self.navigationBar.buttonGroup.updateButtons(sender)
        # 切换界面
        if sender == self.musicGroupButton:
            # 更新配置文件的下标
            self.config['current-index'] = 0
            self.config['pre-index'] = self.parent(
            ).stackedWidget.currentIndex()
            self.parent().stackedWidget.setCurrentWidget(
                self.parent().myMusicInterface)
        elif sender == self.settingButton:
            self.config['current-index'] = 1
            self.config['pre-index'] = self.parent(
            ).stackedWidget.currentIndex()
            self.parent().stackedWidget.setCurrentWidget(
                self.parent().settingInterface)

    def setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\navigation.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def paintEvent(self, e):
        """ 绘制分隔符 """
        painter = QPainter(self)
        #pen = QPen(QColor(214,214,214,240))
        pen = QPen(QColor(160, 160, 160, 240))
        painter.setPen(pen)
        # 前两个参数为第一个坐标，后两个为第二个坐标
        painter.drawLine(15, 346, self.width() - 15, 346)
        painter.drawLine(15,
                         self.height() - 123 - 62,
                         self.width() - 15,
                         self.height() - 123 - 62)
