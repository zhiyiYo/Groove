# coding:utf-8

import sys
from time import time

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QStackedWidget, QWidget

from .tab_button import TabButton
from my_album_tab_interface import AlbumTabInterface
from my_song_tab_interface import SongTabInterface
from my_widget.button_group import ButtonGroup
# from my_songer_tab_interface import SongerTabInterface


class MyMusicTabWidget(QWidget):
    """ 放置歌曲、歌手和专辑界面 """
    currentIndexChanged = pyqtSignal(int)

    def __init__(self, target_path_list: list, parent=None):
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
        t1=time()
        self.songTab = SongTabInterface(self.target_path_list, self)
        t2=time()
        # self.songerTab = SongerTabInterface(self)
        print('创建歌曲标签界面所花时间：'.ljust(17), t2-t1)
        self.albumTab = AlbumTabInterface(self.target_path_list, self)
        t3 = time()
        print('创建专辑标签界面所花时间：'.ljust(17), t3-t2)
        # 实例化按钮和分组
        self.songTabButton = TabButton('歌曲', self, 0)
        self.songerTabButton = TabButton('歌手', self, 1)
        self.albumTabButton = TabButton('专辑', self, 1)
        self.button_list = [self.songTabButton,
                            self.songerTabButton, self.albumTabButton]
        # 实例化布局
        self.v_layout = QVBoxLayout(self)

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(1267, 800)
        self.setStyleSheet('background:white')
        # 将页面添加到stackedWidget中
        self.stackedWidget.addWidget(self.songTab)
        # self.stackedWidget.addWidget(self.songerTab)
        self.stackedWidget.addWidget(self.albumTab)
        # 分配ID
        self.songTabButton.setProperty('name', 'songTabButton')
        # self.songerTabButton.setProperty('name', 'songerTabButton')
        self.albumTabButton.setProperty('name', 'albumTabButton')
        # 设置当前的界面
        self.songTabButton.isSelected = True
        # 将按钮点击信号连接到槽函数
        for button in [self.songTabButton, self.albumTabButton]:
            button.buttonSelected.connect(self.buttonSelectedSlot)

    def initLayout(self):
        """ 初始化布局 """
        self.songTabButton.move(14, 0)
        self.songerTabButton.move(117, 0)
        self.albumTabButton.move(220, 0)
        self.stackedWidget.move(0, 45)

    def resizeEvent(self, QResizeEvent):
        """ 窗口大小改变时同时调整stackedWidget的大小 """
        self.stackedWidget.resize(self.width(), self.height())
        self.songTab.resize(self.size())
        self.albumTab.resize(self.size())

    def buttonSelectedSlot(self, index):
        """ 按钮点击时切换界面 """
        # 如果此时处于选择状态则不切换界面
        if self.songTab.songCardListWidget.isInSelectionMode:
            return
        sender = self.sender()
        self.setSelectedButton(index)
        self.stackedWidget.setCurrentIndex(sender.tabIndex)
        self.currentIndexChanged.emit(sender.tabIndex)

    def paintEvent(self, QPaintEvent):
        """ 绘制背景 """
        super().paintEvent(QPaintEvent)
        painter = QPainter(self)
        pen = QPen(QColor(229, 229, 229))
        painter.setPen(pen)
        painter.drawLine(10, 40, self.width() - 12, 40)

    def setSelectedButton(self, index):
        """ 设置选中的按钮 """
        for button in [self.songTabButton, self.albumTabButton]:
            if button.tabIndex == index:
                button.setSelected(True)
            else:
                button.setSelected(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MyMusicTabWidget(['D:\\KuGou\\test_audio\\'])
    demo.show()
    sys.exit(app.exec_())
