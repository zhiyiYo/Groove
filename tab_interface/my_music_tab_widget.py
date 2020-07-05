# coding:utf-8

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QStackedWidget, QWidget

from .album_tab_interface import AlbumTabInterface
from .song_tab_interface import SongTabInterface
from .songer_tab_interface import SongerTabInterface
from tab_interface.tab_button import TabButton
from my_widget.button_group import ButtonGroup


class MyMusicTabWidget(QWidget):
    """ 放置歌曲、歌手和专辑界面 """

    def __init__(self,target_path_list:list, parent=None):
        super().__init__(parent)
        self.target_path_list = target_path_list
        # 创建小部件
        self.createWidgets()
        # 初始化界面
        self.initWidget()
        self.initLayout()
        
    def createWidgets(self):
        """ 创建小部件 """
        # 实例化界面
        self.stackedWidget = QStackedWidget(self)
        self.songTab = SongTabInterface(self.target_path_list, self)
        self.songerTab = SongerTabInterface(self)
        self.albumTab = AlbumTabInterface(self.target_path_list, self)
        # 实例化按钮和分组
        self.songTabButton = TabButton('歌曲', self, 0)
        self.songerTabButton = TabButton('歌手', self, 1)
        self.albumTabButton = TabButton('专辑', self, 2)
        self.buttonGroup = ButtonGroup()
        self.button_list = [self.songTabButton, self.songerTabButton, self.albumTabButton]
        self.buttonGroup.addButtons(self.button_list)
        # 实例化布局
        self.v_layout = QVBoxLayout(self)
        
    def initWidget(self):
        """ 初始化小部件 """
        self.resize(1267, 800)
        self.setStyleSheet('background:white')
        # 将页面添加到stackedWidget中
        self.stackedWidget.addWidget(self.songTab)
        self.stackedWidget.addWidget(self.songerTab)
        self.stackedWidget.addWidget(self.albumTab)
        # 分配ID
        self.songTabButton.setProperty('name', 'songTabButton')
        self.songerTabButton.setProperty('name', 'songerTabButton')
        self.albumTabButton.setProperty('name', 'albumTabButton')
        # 设置当前的界面
        self.songTabButton.isSelected = True
        # 将按钮点击信号连接到槽函数
        for button in self.button_list:
            button.clicked.connect(self.buttonClickedEvent)
            
    def initLayout(self):
        """ 初始化布局 """
        self.songTabButton.move(14, 0)
        self.songerTabButton.move(117, 0)
        self.albumTabButton.move(220, 0)
        self.stackedWidget.move(0, 45)
        
    def resizeEvent(self, QResizeEvent):
        """ 窗口大小改变时同时调整stackedWidget的大小 """
        self.stackedWidget.resize(self.width(), self.height() - 45)

    def buttonClickedEvent(self):
        """ 按钮点击时切换界面 """
        sender = self.sender()
        self.buttonGroup.updateButtons(sender)
        self.stackedWidget.setCurrentIndex(sender.tabIndex)

    def paintEvent(self, QPaintEvent):
        """ 绘制背景 """
        super().paintEvent(QPaintEvent)
        painter = QPainter(self)
        pen = QPen(QColor(229, 229, 229))
        painter.setPen(pen)
        painter.drawLine(10, 41, self.width() - 12, 41)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MyMusicTabWidget(['D:\\KuGou\\test_audio\\'])
    demo.show()
    sys.exit(app.exec_())
