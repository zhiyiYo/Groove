import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt,QAbstractAnimation,QPropertyAnimation
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QToolButton,QLabel
sys.path.append('..')
from Groove.my_widget.my_button import NavigationButton
from Groove.effects.window_effect import WindowEffect
from Groove.my_widget.my_lineEdit import SearchLineEdit


class NavigationMenu(QWidget):
    """ 侧边导航菜单 """
    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建搜索框
        self.searchLineEdit = SearchLineEdit(self)
        # 创建按钮
        self.createButtons()
        # 创建布局
        self.h_layout_1 = QHBoxLayout()
        self.h_layout_2 = QHBoxLayout()
        self.all_v_layout = QVBoxLayout()
        # 实例化窗口特效
        # self.windowEffect = WindowEffect()
        
        # 初始化界面
        self.initWidget()
        self.initLayout()
        self.setQss()
    
    def createButtons(self):
        """实例化按钮 """
        self.showBarButton = NavigationButton(
            r'resource\images\navigationBar\黑色最大化导航栏.png', parent=self)
        self.musicGroupButton = NavigationButton(
            r'resource\images\navigationBar\黑色我的音乐.png', '我的音乐', self, (400,60), (60, 62))
        self.historyButton = NavigationButton(
            r'resource\images\navigationBar\黑色最近播放.png','最近播放的内容', self, (400,62), (60, 62))
        self.playingButton = NavigationButton(
            r'resource\images\navigationBar\黑色导航栏正在播放.png', '正在播放', self, (400, 62), (60, 62))
        self.playListButton = NavigationButton(
            r'resource\images\navigationBar\黑色播放列表.png', '播放列表', self, (340, 60))
        self.createPlayListButton = NavigationButton(
            r'resource\images\navigationBar\黑色新建播放列表.png', parent=self)
        self.myLoveButton = NavigationButton(
            r'resource\images\navigationBar\黑色我喜欢_60_62.png', '我喜欢', self, (400, 62), (60, 62))
        self.settingButton = NavigationButton(
            r'resource\images\navigationBar\黑色设置按钮.png', '设置', self, (400, 62), (60, 62))
        # 创建一个小部件列表
        self.widget_list = [self.showBarButton, self.searchLineEdit, self.musicGroupButton,
                            self.historyButton, self.playingButton, self.playListButton,
                            self.createPlayListButton, self.myLoveButton, self.settingButton]
        # 创建按钮列表
        self.button_list = [self.showBarButton, self.musicGroupButton, self.historyButton,
                            self.playingButton, self.playListButton,
                            self.myLoveButton, self.settingButton]
                            
    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(400)
        #self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground|Qt.WA_StyledBackground)
        self.setObjectName('navigationMenu')
        # 开启亚克力效果
        self.hWnd = HWND(int(self.winId()))
        #self.windowEffect.setAcrylicEffect(self.hWnd, 'F2F2F25F')
        # 将按钮点击信号连接到槽函数
        for button in self.button_list[1:]:
            button.clicked.connect(self.buttonClickedEvent)
        # 分配ID
        self.myLoveButton.setObjectName('myLoveButton')

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
        self.h_layout_2.addWidget(self.createPlayListButton)
        self.all_v_layout.addLayout(self.h_layout_2)
        self.all_v_layout.addWidget(self.myLoveButton)
        self.all_v_layout.addWidget(self.settingButton, 0, Qt.AlignBottom)
        self.all_v_layout.addSpacing(123)
        # 设置总布局
        self.setLayout(self.all_v_layout)

    def buttonClickedEvent(self):
        """ 按钮点击事件 """
        sender = self.sender()
        if sender != self.createPlayListButton:
            for button in self.button_list:
                if sender == button:
                    button.setProperty('selected', 'true')
                else:
                    button.setProperty('selected', 'false')
            # 更新按钮的样式
            for button in self.button_list:
                button.update()
        
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
        painter.drawLine(15, self.height() - 123 - 62,
                        self.width() - 15, self.height() - 123 - 62)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = NavigationMenu()
    demo.show()
    sys.exit(app.exec_())


    
