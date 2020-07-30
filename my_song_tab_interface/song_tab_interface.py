import sys
import time
from PyQt5.QtCore import QPoint, Qt, QSize, QEvent,pyqtSignal
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,
                             QLayout, QPushButton, QVBoxLayout, QWidget)
from .song_card_list_widget import SongCardListWidget

sys.path.append('..')
from Groove.my_widget.my_menu import Menu
from Groove.my_widget.my_button import RandomPlayButton, SortModeButton


class SongTabInterface(QWidget):
    """ 创建歌曲标签界面 """
    randomPlayAllSig = pyqtSignal()

    def __init__(self, target_path_list:list, parent=None):
        super().__init__(parent)
        self.resize(1267, 804)
        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.all_v_layout = QVBoxLayout()
        # 实例化标签和下拉菜单
        self.sortModeMenu = Menu(parent=self)
        self.sortModeLabel = QLabel('排序依据:', self)
        self.sortModeButton = SortModeButton('添加日期', self.showSortModeMenu, self)
        self.randomPlayButton = RandomPlayButton(slot=self.randomPlay, parent=self)
        # 实例化歌曲列表视图
        self.songCardListWidget = SongCardListWidget(target_path_list)
        # 将动作添加到菜单中
        self.addActionToMenu()
        # 设置初始排序方式
        self.currentSortMode = self.sortByCratedTime
        self.sortModeNum_dict = {'添加日期': 0, 'A到Z': 1, '歌手': 2}
        # 初始化UI界面
        self.initWidget()
        self.initLayout()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件的属性 """
        #self.setWindowFlags(Qt.FramelessWindowHint)
        # 隐藏滚动条
        self.songCardListWidget.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.songCardListWidget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        # 获取歌曲总数
        songs_num = len(self.songCardListWidget.songCard_list)
        self.randomPlayButton.setText(f'({songs_num})')
        # 分配ID
        self.sortModeMenu.setObjectName('sortModeMenu')
        self.sortModeLabel.setObjectName('sortModeLabel')


    def initLayout(self):
        """ 初始化布局 """
        self.h_layout.addWidget(self.randomPlayButton, 0, Qt.AlignLeft)
        self.h_layout.addSpacing(30)
        self.h_layout.addWidget(self.sortModeLabel, 0, Qt.AlignLeft)
        self.h_layout.addWidget(self.sortModeButton, 0, Qt.AlignLeft)
        # 不给按钮和标签分配多余的空间
        self.h_layout.addStretch(1)

        self.all_v_layout.addSpacing(7)
        self.all_v_layout.addLayout(self.h_layout)
        self.all_v_layout.addSpacing(7)
        self.all_v_layout.addWidget(self.songCardListWidget)
        self.setLayout(self.all_v_layout)

    def addActionToMenu(self):
        """ 将动作添加到菜单里 """
        # 创建排序列表项目的动作
        self.sortBySonger = QAction('歌手', self, triggered=self.sortSongCard)
        self.sortByDictOrder = QAction(
            'A到Z', self, triggered=self.sortSongCard)
        self.sortByCratedTime = QAction(
            '添加日期', self, triggered=self.sortSongCard)
        # 将动作添加到菜单中
        self.sortModeMenu.addActions(
            [self.sortByCratedTime, self.sortByDictOrder, self.sortBySonger])

    def randomPlay(self):
        """ 刷新并随机排列播放列表 """
        self.randomPlayAllSig.emit()

    def sortSongCard(self):
        """ 根据所选的排序方式对歌曲卡进行重新排序 """
        sender = self.sender()
        self.currentSortMode = sender
        # 清空旧的列表
        self.songCardListWidget.clear()
        self.songCardListWidget.item_list.clear()
        self.songCardListWidget.songCard_list.clear()
        # 清除选中item
        self.songCardListWidget.preItem = None
        # 更新列表
        if sender == self.sortByCratedTime:
            self.sortModeButton.setText('添加时间')
            # 重置排序方法
            self.songCardListWidget.sortMode = '添加时间'
            self.songCardListWidget.addListWidgetItem()
        elif sender == self.sortByDictOrder:
            self.sortModeButton.setText('A到Z')
            self.songCardListWidget.sortMode = 'A到Z'
            self.songCardListWidget.addListWidgetItem()
        else:
            self.sortModeButton.setText('歌手')
            self.songCardListWidget.sortMode = '歌手'
            self.songCardListWidget.addListWidgetItem()

    def showSortModeMenu(self):
        """ 显示排序方式菜单 """
        # 设置默认动作
        self.sortModeMenu.setDefaultAction(self.currentSortMode)
        self.sortModeMenu.exec(
            self.mapToGlobal(QPoint(self.sortModeButton.x(),
                                    self.sortModeButton.y() - 37*self.sortModeNum_dict[self.currentSortMode.text()]-1)))

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\songTabInterface.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mySongTab = SongTabInterface(['D:\\KuGou'])
    mySongTab.show()
    sys.exit(app.exec_())
