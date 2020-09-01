# coding:utf-8

from time import time

from PyQt5.QtCore import QEvent, QPoint, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QLabel, QPushButton, QWidget

from my_widget.my_button import RandomPlayButton, SortModeButton
from my_widget.my_menu import AeroMenu

from .album_card_viewer import AlbumCardViewer


class AlbumTabInterface(QWidget):
    """ 定义专辑卡标签界面 """
    randomPlayAllSig = pyqtSignal()
    sortModeChanged = pyqtSignal()
    columnChanged = pyqtSignal()

    def __init__(self, target_path_list: list, parent=None):
        super().__init__(parent)
        self.resize(1270, 800)
        # 实例化专辑视图
        t1 = time()
        self.albumCardViewer = AlbumCardViewer(target_path_list, self)
        t2 = time()
        print('创建专辑视图所花时间：'.ljust(19), t2-t1)
        self.guideLabel = QLabel('这里没有可显示的内容。请尝试其他筛选器。', self)
        # 实例化无序播放所有按钮
        self.randomPlayButton = RandomPlayButton(
            slot=self.randomPlay, parent=self)
        # 实例化排序依据标签、按钮和菜单
        self.sortModeMenu = AeroMenu(parent=self)
        self.sortModeLabel = QLabel('排序依据:', self)
        self.sortModeButton = SortModeButton(
            '添加日期', self.showSortModeMenu, self)
        # 将动作添加到菜单中
        self.addActionToMenu()
        # 设置初始排序方式
        self.currentSortMode = self.sortByCratedTime
        self.sortModeNum_dict = {'添加日期': 0, 'A到Z': 1, '发行年份': 2, '歌手': 3}
        # 初始化
        self.__initWidget()
        self.__initLayout()

    def __initWidget(self):
        """ 初始化小部件 """
        # 获取专辑总数
        albums_num = len(self.albumCardViewer.albumCardDict_list)
        self.randomPlayButton.setText(f'({albums_num})')
        # 分配ID
        self.setObjectName('albumTabInterface')
        self.sortModeMenu.setObjectName('sortModeMenu')
        self.sortModeLabel.setObjectName('sortModeLabel')
        self.sortModeMenu.setProperty('modeNumber', '4')
        self.guideLabel.setObjectName('guideLabel')
        self.guideLabel.resize(500, 30)
        # 如果专辑为空就显示guideLabel
        self.guideLabel.setHidden(not self.albumCardViewer.isAlbumEmpty)
        if self.albumCardViewer.isAlbumEmpty:
            self.sortModeButton.setEnabled(False)
        # 设置层叠样式
        self.__setQss()
        # 信号连接到槽函数
        self.albumCardViewer.columnChanged.connect(self.columnChanged)

    def __initLayout(self):
        """ 初始化布局 """
        self.guideLabel.move(15, 103)
        self.randomPlayButton.move(11, 23)
        self.sortModeLabel.move(211, 23)
        self.sortModeButton.move(286, 18)
        self.albumCardViewer.move(0, 56)

    def addActionToMenu(self):
        """ 将动作添加到菜单里 """

        # 创建排序列表项目的动作
        self.sortByDictOrder = QAction(
            'A到Z', self, triggered=self.sortAlbumCard)
        self.sortByCratedTime = QAction(
            '添加日期', self, triggered=self.sortAlbumCard)
        self.sortByYear = QAction('发行年份', self, triggered=self.sortAlbumCard)
        self.sortBySonger = QAction('歌手', self, triggered=self.sortAlbumCard)
        # 设置动作的悬浮提醒
        self.sortByCratedTime.setToolTip('添加时间')
        self.sortByDictOrder.setToolTip('A到Z')
        self.sortByYear.setToolTip('发行年份')
        self.sortBySonger.setToolTip('歌手')

        # 将动作添加到菜单中
        self.sortModeMenu.addActions(
            [self.sortByCratedTime, self.sortByDictOrder, self.sortByYear, self.sortBySonger])

    def randomPlay(self):
        """ 刷新并随机排列播放列表 """
        self.randomPlayAllSig.emit()

    def sortAlbumCard(self):
        """ 根据所选的排序方式对歌曲卡进行重新排序 """
        sender = self.sender()
        self.currentSortMode = sender
        self.albumCardViewer.albumViewWidget.albumBlurBackground.hide()
        # 更新分组
        if sender == self.sortByCratedTime and self.albumCardViewer.sortMode != '添加时间':
            self.sortModeButton.setText('添加时间')
            self.albumCardViewer.sortByAddTimeGroup()
        elif sender == self.sortByDictOrder and self.albumCardViewer.sortMode != 'A到Z':
            self.sortModeButton.setText('A到Z')
            self.albumCardViewer.sortMode = 'A到Z'
            self.albumCardViewer.sortByFirsetLetter()
        elif sender == self.sortByYear and self.albumCardViewer.sortMode != '发行年份':
            self.sortModeButton.setText('发行年份')
            self.albumCardViewer.sortMode = '发行年份'
            self.albumCardViewer.sortByYear()
        elif sender == self.sortBySonger and self.albumCardViewer.sortMode != '歌手':
            self.sortModeButton.setText('歌手')
            self.albumCardViewer.sortMode = '歌手'
            self.albumCardViewer.sortBySonger()
        # 改变排序方式时发送信号调整关联滚动条的滚动范围
        self.sortModeChanged.emit()

    def showSortModeMenu(self):
        """ 显示排序方式菜单 """
        # 设置默认动作
        self.sortModeMenu.setDefaultAction(self.currentSortMode)
        self.sortModeMenu.exec(
            self.mapToGlobal(QPoint(self.sortModeButton.x(),
                                    self.sortModeButton.y() - 37*self.sortModeNum_dict[self.currentSortMode.text()]-1)))

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumTabInterface.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def resizeEvent(self, e):
        """ 调整大小时改变小部件大小 """
        super().resizeEvent(e)
        self.albumCardViewer.resize(
            self.width(), self.albumCardViewer.height())


