import sys
from time import time

from PyQt5.QtCore import QEvent, QPoint, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent
from PyQt5.QtWidgets import QAction, QApplication, QLabel, QWidget

from my_widget.my_button import RandomPlayButton, SortModeButton
from my_widget.my_menu import AeroMenu

from .song_card_list_widget import SongCardListWidget


class SongTabInterface(QWidget):
    """ 创建歌曲标签界面 """
    randomPlayAllSig = pyqtSignal()

    def __init__(self, target_path_list: list, parent=None):
        super().__init__(parent)
        self.resize(1267, 804)
        # 实例化标签和下拉菜单
        self.sortModeMenu = AeroMenu(parent=self)
        self.sortModeLabel = QLabel('排序依据:', self)
        self.guideLabel = QLabel('这里没有可显示的内容。请尝试其他筛选器。', self)
        self.sortModeButton = SortModeButton(
            '添加日期', self.showSortModeMenu, self)
        self.randomPlayButton = RandomPlayButton(
            slot=self.randomPlay, parent=self)
        # 实例化歌曲列表视图
        t1 = time()
        self.songCardListWidget = SongCardListWidget(target_path_list, self)
        t2 = time()
        print('创建歌曲卡列表视图所花时间：'.ljust(16), t2 - t1)
        # 将动作添加到菜单中
        self.__addActionToMenu()
        # 设置初始排序方式
        self.currentSortMode = self.sortByCratedTime
        self.sortModeNum_dict = {'添加日期': 0, 'A到Z': 1, '歌手': 2}
        # 初始化界面
        self.__initWidget()
        self.__initLayout()
        self.__setQss()

    def __initWidget(self):
        """ 初始化小部件的属性 """
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
        self.guideLabel.setObjectName('guideLabel')
        # 根据歌曲卡个数决定是否隐藏标签
        self.guideLabel.resize(500, 26)
        if self.songCardListWidget.songCard_list:
            self.guideLabel.hide()
        else:
            self.songCardListWidget.hide()
            self.guideLabel.show()

    def __initLayout(self):
        """ 初始化布局 """
        self.guideLabel.move(15, 105)
        self.randomPlayButton.move(11, 18)
        self.sortModeLabel.move(211, 23)
        self.sortModeButton.move(286, 18)
        self.songCardListWidget.move(9, 60)

    def __addActionToMenu(self):
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
        # 更新列表
        if sender == self.sortByCratedTime:
            self.sortModeButton.setText('添加时间')
            self.songCardListWidget.setSortMode('添加时间')
        elif sender == self.sortByDictOrder:
            self.sortModeButton.setText('A到Z')
            self.songCardListWidget.setSortMode('A到Z')
        else:
            self.sortModeButton.setText('歌手')
            self.songCardListWidget.setSortMode('歌手')

    def showSortModeMenu(self):
        """ 显示排序方式菜单 """
        # 设置默认动作
        self.sortModeMenu.setDefaultAction(self.currentSortMode)
        self.sortModeMenu.exec(
            self.mapToGlobal(QPoint(self.sortModeButton.x(),
                                    self.sortModeButton.y() - 37*self.sortModeNum_dict[self.currentSortMode.text()]-1)))

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\songTabInterface.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def resizeEvent(self, e):
        """ 改变窗口大小时也调整部件大小 """
        super().resizeEvent(e)
        self.songCardListWidget.resize(
            self.width() - 20, self.songCardListWidget.height())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mySongTab = SongTabInterface(['D:\\KuGou'])
    mySongTab.show()
    sys.exit(app.exec_())
