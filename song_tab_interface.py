import sys
import time
from PyQt5.QtCore import QPoint, Qt, QSize, QEvent
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,
                             QLayout, QMenu, QPushButton, QVBoxLayout, QWidget)

from song_card_list_widget import SongCardListWidget
from getfont import onLoadFont


class SongTabInterface(QWidget):
    """ 创建歌曲标签界面 """

    def __init__(self, songs_folder, parent=None):
        super().__init__(parent)

        self.resize(1267, 684)
        # 创建一个存储播放模式的标志位，4、3、1分别对应随机播放、列表循环、单曲循环
        #self.loopMode = 4

        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.all_v_layout = QVBoxLayout()

        # 实例化标签和下拉菜单
        self.sortModeMenu = QMenu(self)
        self.sortModeLabel = QLabel('排序依据:', self)
        self.sortModeButton = QPushButton('添加日期', self)
        self.loopModeButton = QPushButton(
            QIcon('resource\\images\\无序播放所有_130_17.png'), '', self)
        self.loopModeButton.setIconSize(QSize(130,17))

        # 实例化歌曲列表视图
        self.songCardListWidget = SongCardListWidget(songs_folder)

        # 将动作添加到菜单中
        self.addActionToMenu()

        # 设置初始排序方式
        self.currentSortMode = self.sortByCratedTime
        # 初始化UI界面
        self.initWidget()
        self.initLayout()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件的属性 """

        #获取歌曲总数
        songs_num = len(self.songCardListWidget.song_card_list)
        self.loopModeButton.setText(f'({songs_num})')

        # 设置鼠标光标
        self.sortModeButton.setCursor(Qt.PointingHandCursor)
        self.loopModeButton.setCursor(Qt.PointingHandCursor)

        # 分配ID
        self.sortModeMenu.setObjectName('sortModeMenu')
        self.sortModeLabel.setObjectName('sortModeLabel')
        self.sortModeButton.setObjectName('sortModeButton')
        self.loopModeButton.setObjectName('loopModeButton')

        # 将信号连接到槽函数
        self.loopModeButton.clicked.connect(self.changeLoopMode)
        self.sortModeButton.clicked.connect(self.showSortModeMenu)

        # 给loopModeButton设置监听
        self.loopModeButton.installEventFilter(self)

    def initLayout(self):
        """ 初始化布局 """

        self.h_layout.addWidget(self.loopModeButton, 0, Qt.AlignLeft)
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

        # 设置动作的悬浮提醒
        self.sortByCratedTime.setToolTip('添加时间')
        self.sortByDictOrder.setToolTip('A到Z')
        self.sortBySonger.setToolTip('歌手')

        # 将动作添加到菜单中
        self.sortModeMenu.addActions(
            [self.sortByCratedTime, self.sortByDictOrder, self.sortBySonger])

    def changeLoopMode(self):
        """ 改变播放的循环模式 """
        pass

    def sortSongCard(self):
        """ 根据所选的排序方式对歌曲卡进行重新排序 """
        sender = self.sender()
        self.currentSortMode = sender
        # 清空旧的列表
        self.songCardListWidget.clear()
        self.songCardListWidget.item_list.clear()
        self.songCardListWidget.song_card_list.clear()
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
            self.mapToGlobal(QPoint(self.sortModeButton.x(), self.sortModeButton.y() - 5)))

    def setQss(self):
        """ 设置层叠样式 """

        with open('resource\\css\\initSongCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def eventFilter(self, obj, event):
        """ 当鼠标移到播放模式按钮上时更换图标 """
        if obj == self.loopModeButton:
            if event.type() == QEvent.Enter or event.type() == QEvent.HoverMove:
                self.loopModeButton.setIcon(
                    QIcon('resource\\images\\无序播放所有_hover_130_17.png'))
            elif event.type() == QEvent.Leave:
                self.loopModeButton.setIcon(
                    QIcon('resource\\images\\无序播放所有_130_17.png'))

        return QWidget.eventFilter(self, obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mySongTab = SongTabInterface('D:\\KuGou')
    mySongTab.show()

    sys.exit(app.exec_())
