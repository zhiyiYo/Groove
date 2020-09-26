# coding:utf-8

import pinyin
from my_widget.my_button import ThreeStateButton
from my_widget.my_grid_layout import GridLayout
from my_widget.my_menu import AeroMenu
from my_widget.my_scrollArea import ScrollArea
from PyQt5.QtCore import (QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          Qt, pyqtSignal)
from PyQt5.QtWidgets import QAction, QLabel, QPushButton, QWidget

from .blur_background import BlurBackground
from .playlist_card import PlaylistCard
from .selection_mode_bar import SelectionModeBar


class PlaylistCardInterface(QWidget):
    """ 播放列表卡界面 """
    selectionModeStateChanged = pyqtSignal(bool)

    def __init__(self, playlists: list, parent=None):
        super().__init__(parent)
        self.columnNum = 1
        self.sortMode = '修改日期'
        self.playlists = playlists
        self.playlistCard_list = []
        self.playlistCardDict_list = []  # type:list[dict]
        self.checkedPlaylistCard_list = []
        self.isInSelectionMode = False
        self.isAllPlaylistCardChecked = False
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        # 创建磨砂背景
        self.scrollArea = ScrollArea(self)
        self.scrollWidget = QWidget(self)
        self.gridLayout = GridLayout()
        self.blurBackground = BlurBackground(self.scrollWidget)
        # 创建播放列表卡
        self.__createPlaylistCards()
        # 创建白色遮罩
        self.whiteMask = QWidget(self)
        self.sortModeLabel = QLabel('排序依据:', self)
        self.playlistLabel = QLabel('播放列表', self)
        self.sortModeButton = QPushButton('修改日期', self)
        self.createPlaylistButton = ThreeStateButton(
            {'normal': r'resource\images\playlist_interface\newPlaylist_normal.png',
             'hover': r'resource\images\playlist_interface\newPlaylist_hover.png',
             'pressed': r'resource\images\playlist_interface\newPlaylist_pressed.png'}, self, (129, 19))
        # 创建导航标签
        self.guideLabel = QLabel('这里没有可显示的内容。请尝试其他筛选器。', self)
        self.guideLabel.setStyleSheet(
            "color: black; font: 25px 'Microsoft YaHei'")
        self.guideLabel.resize(500, 26)
        self.guideLabel.move(35, 286)
        # 创建排序菜单
        self.sortModeMenu = AeroMenu(parent=self)
        self.sortByModifiedTimeAct = QAction(
            '修改时间', self, triggered=lambda: self.__sortPlaylist('modifiedTime'))
        self.sortByAToZAct = QAction(
            'A到Z', self, triggered=lambda: self.__sortPlaylist('AToZ'))
        self.sortAct_list = [self.sortByModifiedTimeAct, self.sortByAToZAct]
        # 创建选择状态栏
        self.selectionModeBar = SelectionModeBar(self)
        # 记录当前的排序方式
        self.currentSortAct = self.sortByModifiedTimeAct

    def __createPlaylistCards(self):
        """ 创建播放列表卡 """
        # 创建并行动画组
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAni_list = []
        for playlist in self.playlists:
            self.__appendOnePlaylistCard(playlist)

    def __appendOnePlaylistCard(self, playlist: dict):
        """ 创建一个播放列表卡 """
        playlistCard = PlaylistCard(playlist, self)
        self.playlistCard_list.append(playlistCard)
        self.playlistCardDict_list.append(
            {'playlistCard': playlistCard, 'playlist': playlist})
        # 创建动画
        hideCheckBoxAni = QPropertyAnimation(
            playlistCard.checkBoxOpacityEffect, b'opacity')
        self.hideCheckBoxAniGroup.addAnimation(hideCheckBoxAni)
        self.hideCheckBoxAni_list.append(hideCheckBoxAni)
        # 信号连接到槽
        playlistCard.showBlurBackgroundSig.connect(self.__showBlurBackground)
        playlistCard.hideBlurBackgroundSig.connect(self.blurBackground.hide)
        playlistCard.checkedStateChanged.connect(
            self.__playlistCardCheckedStateChangedSlot)
        playlistCard

    def __initWidget(self):
        """ 初始化小部件 """
        # 隐藏小部件
        self.blurBackground.hide()
        self.selectionModeBar.hide()
        self.guideLabel.setHidden(bool(self.playlistCard_list))
        # 初始化滚动条
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        # 将动作添加到菜单中
        self.sortModeMenu.addActions(self.sortAct_list)
        # 分配ID和属性
        self.scrollWidget.setObjectName('scrollWidget')
        self.playlistLabel.setObjectName('playlistLabel')
        self.sortModeLabel.setObjectName('sortModeLabel')
        self.sortModeButton.setObjectName('sortModeButton')
        self.sortModeMenu.setObjectName('sortModeMenu')
        self.sortModeMenu.setProperty('modeNumber', '2')
        self.__setQss()
        self.__initLayout()
        self.resize(1270, 760)
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ 初始化布局 """
        self.scrollArea.move(0, 0)
        self.playlistLabel.move(30, 54)
        self.sortModeLabel.move(190, 135)
        self.sortModeButton.move(264, 130)
        self.createPlaylistButton.move(30, 135)
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())
        # 设置布局的间距和外边距
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setContentsMargins(15, 175, 15, 120)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollWidget.setLayout(self.gridLayout)
        # 如果没有播放列表就直接返回
        if not self.playlistCard_list:
            return
        # 按照修改日期排序播放列表
        self.__sortPlaylist('modifiedTime')

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\playlistCardInterface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 调整小部件尺寸和位置 """
        super().resizeEvent(e)
        self.scrollArea.resize(self.size())
        self.whiteMask.resize(self.width() - 15, 175)
        self.scrollArea.verticalScrollBar().resize(4, self.height() - 116)
        self.scrollArea.verticalScrollBar().move(-1, 40)
        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        if self.width() < 641 and self.columnNum != 1:
            self.__setColumnNum(1)
        elif 641 <= self.width() < 954 and self.columnNum != 2:
            self.__setColumnNum(2)
        elif 954 <= self.width() < 1267 and self.columnNum != 3:
            self.__setColumnNum(3)
        elif 1267 <= self.width() < 1580 and self.columnNum != 4:
            self.__setColumnNum(4)
        elif 1580 <= self.width() < 1893 and self.columnNum != 5:
            self.__setColumnNum(5)
        elif self.width() >= 1893 and self.columnNum != 6:
            self.__setColumnNum(6)

    def __setColumnNum(self, columnNum: int):
        """ 设置网格列数 """
        self.columnNum = columnNum
        self.gridLayout.updateColumnNum(columnNum, 298, 288)
        self.scrollWidget.resize(
            self.width(), 175 + self.gridLayout.rowCount() * 298 + 120)

    def __sortPlaylist(self, key):
        """ 排序播放列表 """
        # 更新按钮文本
        if key == 'modifiedTime':
            self.sortMode = '修改时间'
            self.currentSortAct = self.sortByModifiedTimeAct
            self.playlistCardDict_list.sort(
                key=self.__sortPlaylistByModifiedTime, reverse=True)
        else:
            self.sortMode = 'A到Z'
            self.currentSortAct = self.sortByAToZAct
            self.playlistCardDict_list.sort(
                key=self.__sortPlaylistByAToZ, reverse=False)
        self.sortModeButton.setText(self.sortMode)
        # 先将小部件布局中移除
        self.gridLayout.removeAllWidgets()
        # 将小部件添加到布局中
        for index, playlistCard_dict in enumerate(self.playlistCardDict_list):
            row = index // self.columnNum
            column = index - self.columnNum * row
            playlistCard = playlistCard_dict['playlistCard']
            self.gridLayout.addWidget(playlistCard, row, column, Qt.AlignLeft)

    def __showBlurBackground(self, pos: QPoint, playlistCoverPath: str):
        """ 显示磨砂背景 """
        # 将全局坐标转换为窗口坐标
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.blurBackground.setBlurPic(playlistCoverPath, 40)
        self.blurBackground.move(pos.x() - 30, pos.y() - 20)
        self.blurBackground.show()

    def __showSortModeMenu(self):
        """ 显示排序方式菜单 """
        # 设置默认选中动作
        self.sortModeMenu.setDefaultAction(self.currentSortAct)
        actIndex = self.sortAct_list.index(self.currentSortAct)
        self.sortModeMenu.exec(
            self.mapToGlobal(QPoint(self.sender().x(),
                                    self.sender().y() - 37 * actIndex - 1)))

    def __playlistCardCheckedStateChangedSlot(self, playlistCard: PlaylistCard, isChecked: bool):
        """ 播放列表卡选中状态改变槽函数 """
        # 如果专辑信息不在选中的专辑信息列表中且对应的专辑卡变为选中状态就将专辑信息添加到列表中
        if playlistCard not in self.checkedPlaylistCard_list and isChecked:
            self.checkedPlaylistCard_list.append(playlistCard)
            self.__checkPlaylistCardNumChangedSlot(
                len(self.checkedPlaylistCard_list))
        # 如果专辑信息已经在列表中且该专辑卡变为非选中状态就弹出该专辑信息
        elif playlistCard in self.checkedPlaylistCard_list and not isChecked:
            self.checkedPlaylistCard_list.pop(
                self.checkedPlaylistCard_list.index(playlistCard))
            self.__checkPlaylistCardNumChangedSlot(
                len(self.checkedPlaylistCard_list))
        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            # 所有专辑卡进入选择模式
            self.__setAllPlaylistCardSelectionModeOpen(True)
            # 发送信号要求主窗口隐藏播放栏
            self.selectionModeStateChanged.emit(True)
            self.selectionModeBar.show()
            # 更新标志位
            self.isInSelectionMode = True
        else:
            if not self.checkedPlaylistCard_list:
                # 所有专辑卡退出选择模式
                self.__setAllPlaylistCardSelectionModeOpen(False)
                # 发送信号要求主窗口显示播放栏
                self.selectionModeBar.hide()
                self.selectionModeStateChanged.emit(False)
                # 更新标志位
                self.isInSelectionMode = False

    def __setAllPlaylistCardSelectionModeOpen(self, isOpenSelectionMode: bool):
        """ 设置所有播放列表卡是否进入选择模式 """
        for playlistCard in self.playlistCard_list:
            playlistCard.setSelectionModeOpen(isOpenSelectionMode)
        # 退出选择模式时开启隐藏所有复选框的动画
        if not isOpenSelectionMode:
            self.__startHideCheckBoxAni()

    def __startHideCheckBoxAni(self):
        """ 开始隐藏复选框动画 """
        for ani in self.hideCheckBoxAni_list:
            ani.setStartValue(1)
            ani.setEndValue(0)
            ani.setDuration(140)
        self.hideCheckBoxAniGroup.start()

    def __hideAllCheckBox(self):
        """ 隐藏所有复选框 """
        for playlistCard in self.playlistCard_list:
            playlistCard.checkBox.hide()

    def __unCheckPlaylistCards(self):
        """ 取消所有已处于选中状态的播放列表卡的选中状态 """
        checkedPlaylistCard_list_copy = self.checkedPlaylistCard_list.copy()
        for playlistCard in checkedPlaylistCard_list_copy:
            playlistCard.setChecked(False)
        # 更新按钮的图标为全选
        self.selectionModeBar.checkAllButton.setCheckedState(True)

    def setAllPlaylistCardCheckedState(self, isAllChecked: bool):
        """ 设置所有的专辑卡checked状态 """
        if self.isAllPlaylistCardChecked == isAllChecked:
            return
        self.isAllPlaylistCardChecked = isAllChecked
        for playlistCard in self.playlistCard_list:
            playlistCard.setChecked(isAllChecked)

    def __checkPlaylistCardNumChangedSlot(self, num: int):
        """ 选中的歌曲卡数量改变对应的槽函数 """
        self.selectionModeBar.setPartButtonHidden(num > 1)
        self.selectionModeBar.move(
            0, self.height() - self.selectionModeBar.height())

    def __checkAllButtonSlot(self):
        """ 全选/取消全选按钮槽函数 """
        self.setAllPlaylistCardCheckedState(not self.isAllPlaylistCardChecked)

    def __connectSignalToSlot(self):
        """ 将信号连接到槽 """
        self.sortModeButton.clicked.connect(self.__showSortModeMenu)
        self.selectionModeBar.cancelButton.clicked.connect(
            self.__unCheckPlaylistCards)
        self.selectionModeBar.checkAllButton.clicked.connect(
            self.__checkAllButtonSlot)

    def __sortPlaylistByModifiedTime(self, playlistCard_dict: dict) -> str:
        return playlistCard_dict['playlist']['modifiedTime']

    def __sortPlaylistByAToZ(self, playlistCard_dict: dict) -> str:
        return pinyin.get_initial(playlistCard_dict['playlist']['playlistName'])[0].lower()
