# coding:utf-8

import re

import pinyin
from PyQt5.QtCore import (QEvent, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, pyqtSignal)
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QScrollArea,
    QVBoxLayout, QWidget)

from my_album_tab_interface.album_card import AlbumCard
from .album_blur_background import AlbumBlurBackground
from my_widget.my_groupBox import GroupBox
from my_widget.my_scrollArea import ScrollArea


class AlbumCardViewer(QWidget):
    """ 定义一个专辑卡视图 """
    columnChanged = pyqtSignal()
    playSignal = pyqtSignal(list)
    nextPlaySignal = pyqtSignal(list)
    addAlbumToPlaylistSignal = pyqtSignal(list)
    switchToAlbumInterfaceSig = pyqtSignal(dict)
    saveAlbumInfoSig = pyqtSignal(dict, dict)
    selectionModeStateChanged = pyqtSignal(bool)
    checkedAlbumCardNumChanged = pyqtSignal(int)

    def __init__(self, albumInfo_list: list, parent=None):
        super().__init__(parent)
        self.albumInfo_list = albumInfo_list
        # 初始化网格的列数
        self.column_num = 5
        self.total_row_num = 0
        self.albumCardDict_list = []
        self.albumCard_list = []
        self.checkedAlbumCard_list = []
        # 初始化标志位
        self.isInSelectionMode = False
        self.isAllAlbumCardsChecked = False
        # 设置当前排序方式
        self.sortMode = '添加时间'
        self.__currentSortFunc = self.sortByAddTimeGroup
        # 实例化布局
        self.albumView_hLayout = QHBoxLayout()
        self.all_h_layout = QHBoxLayout()
        # 实例化滚动区域和滚动区域的窗口
        self.__createGuideLabel()
        self.scrollArea = ScrollArea(self)
        self.albumViewWidget = QWidget()
        self.albumBlurBackground = AlbumBlurBackground(self.albumViewWidget)
        # 创建专辑卡并将其添加到布局中
        self.__createAlbumCards()
        # 初始化小部件
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1270, 760)
        # 隐藏磨砂背景
        self.albumBlurBackground.hide()
        # 设置导航标签的可见性
        self.guideLabel.setHidden(bool(self.albumCard_list))
        # 设置滚动区域外边距
        self.scrollArea.setViewportMargins(0, 245, 0, 0)
        # 初始化滚动条
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.albumViewWidget.setObjectName('albumViewWidget')
        self.__connectSignalToSlot()
        self.__initLayout()
        self.__setQss()

    def __createGuideLabel(self):
        """ 创建导航标签 """
        self.guideLabel = QLabel('这里没有可显示的内容。请尝试其他筛选器。', self)
        self.guideLabel.setStyleSheet(
            "color: black; font: 25px 'Microsoft YaHei'")
        self.guideLabel.resize(500, 26)
        self.guideLabel.move(35, 286)

    def __createAlbumCards(self):
        """ 将专辑卡添加到窗口中 """
        # 创建并行动画组
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAni_list = []
        for albumInfo_dict in self.albumInfo_list:
            # 实例化专辑卡和动画
            albumCard = AlbumCard(albumInfo_dict, self)
            # 创建动画
            hideCheckBoxAni = QPropertyAnimation(
                albumCard.checkBoxOpacityEffect, b'opacity')
            self.hideCheckBoxAniGroup.addAnimation(hideCheckBoxAni)
            self.hideCheckBoxAni_list.append(hideCheckBoxAni)
            # 将含有专辑卡及其信息的字典插入列表
            album = albumInfo_dict['album']
            self.albumCard_list.append(albumCard)
            self.albumCardDict_list.append({'albumCard': albumCard,
                                            'albumName': album,
                                            'year': albumInfo_dict['year'][:4],
                                            'songer': albumInfo_dict['songer'],
                                            'firstLetter': pinyin.get_initial(album[0])[0].upper()})

    def __connectSignalToSlot(self):
        """ 将信号连接到槽函数 """
        # 动画完成隐藏复选框
        self.hideCheckBoxAniGroup.finished.connect(self.__hideAllCheckBox)
        for albumCard in self.albumCard_list:
            # 播放
            albumCard.playSignal.connect(self.playSignal)
            # 下一首播放
            albumCard.nextPlaySignal.connect(self.nextPlaySignal)
            # 添加到播放列表
            albumCard.addToPlaylistSignal.connect(
                self.addAlbumToPlaylistSignal)
            # 进入专辑界面
            albumCard.switchToAlbumInterfaceSig.connect(
                self.switchToAlbumInterfaceSig)
            # 更新专辑信息
            albumCard.saveAlbumInfoSig.connect(self.saveAlbumInfoSig)
            # 进入选择模式
            albumCard.checkedStateChanged.connect(
                self.__albumCardCheckedStateChangedSlot)
            # 显示和隐藏磨砂背景
            albumCard.showBlurAlbumBackgroundSig.connect(
                self.__showBlurAlbumBackground)
            albumCard.hideBlurAlbumBackgroundSig.connect(
                self.albumBlurBackground.hide)

    def __initLayout(self):
        """ 初始化布局 """
        # 如果没有专辑，就置位专辑为空标志位并直接返回
        if not self.albumCard_list:
            return
        # 按照添加时间分组
        self.sortByAddTimeGroup()
        self.albumViewWidget.setLayout(self.albumView_hLayout)
        self.scrollArea.setWidget(self.albumViewWidget)
        # 设置全局布局
        self.all_h_layout.addWidget(self.scrollArea)
        self.all_h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.all_h_layout)

    def __updateGridLayout(self):
        """ 更新网格 """
        self.vertical_spacing_count = len(self.currentGroupDict_list)-1
        for currentGroup_dict in self.currentGroupDict_list:
            # 引用当前分组的网格布局
            gridLayout = currentGroup_dict['gridLayout']  # type:QGridLayout
            gridIndex = self.currentGroupDict_list.index(currentGroup_dict)
            columns = range(self.column_num)
            # 补上底部播放栏的占位
            rows = range(
                (len(currentGroup_dict['album_list']) - 1) // self.column_num + 1 +
                int(gridIndex == len(self.currentGroupDict_list) - 1))

            self.current_row_num = max(rows) + 1
            # 设置网格大小
            for column in columns:
                gridLayout.setColumnMinimumWidth(column, 211)
            for row in rows:
                height = 292 if row != max(rows) or gridIndex != len(
                    self.currentGroupDict_list) - 1 else 146
                gridLayout.setRowMinimumHeight(row, height)

            for index, albumCard in enumerate(currentGroup_dict['album_list']):
                x = index // self.column_num
                y = index - self.column_num * x
                if x == max(rows) - 1 and gridIndex == len(self.currentGroupDict_list) - 1:
                    # 多占一行播放栏的位置
                    gridLayout.addWidget(
                        albumCard, x, y, 2, 1, Qt.AlignTop | Qt.AlignLeft)
                else:
                    gridLayout.addWidget(albumCard, x, y, 1, 1, Qt.AlignLeft)
            gridLayout.setAlignment(Qt.AlignLeft)
            # 获取当前的总行数
            self.total_row_num = self.current_row_num
            # 如果现在的总行数小于网格的总行数，就将多出来的行宽度的最小值设为0
            for i in range(gridLayout.rowCount() - 1, self.current_row_num - 1, -1):
                gridLayout.setRowMinimumHeight(i, 0)

            # 如果现在的总列数小于网格的总列数，就将多出来的列的宽度的最小值设置为0
            for i in range(gridLayout.columnCount() - 1, self.column_num - 1, -1):
                gridLayout.setColumnMinimumWidth(i, 0)

        self.albumViewWidget.setFixedWidth(self.width())
        if self.sortMode == '添加时间':
            self.albumViewWidget.setFixedHeight(303 * self.total_row_num)
        else:
            # 补上分组标题所占的高度
            self.albumViewWidget.setFixedHeight(
                303 * self.total_row_num + 34 * len(self.currentGroupDict_list))

    def resizeEvent(self, event):
        """ 根据宽度调整网格的列数 """
        super().resizeEvent(event)
        # 如果第一次超过1337就调整网格的列数
        if self.width() >= 1790 and self.column_num != 8:
            self.__updateColumnNum(8)
        if 1570<=self.width() < 1790 and self.column_num != 7:
            self.__updateColumnNum(7)
        elif 1350<=self.width() < 1570 and self.column_num != 6:
            self.__updateColumnNum(6)
        elif 1130 < self.width() < 1350 and self.column_num != 5:
            self.__updateColumnNum(5)
        elif 910 < self.width() <= 1130 and self.column_num != 4:
            self.__updateColumnNum(4)
        elif 690 < self.width() <= 910:
            self.__updateColumnNum(3)
        elif self.width() <= 690:
            self.__updateColumnNum(2)
        # 调整滚动条
        self.scrollArea.verticalScrollBar().move(-1, 40)
        self.scrollArea.verticalScrollBar().resize(
            self.scrollArea.verticalScrollBar().width(), self.height() - 156)

    def __updateColumnNum(self, new_column):
        """ 更新网格列数 """
        for currentGroup_dict in self.currentGroupDict_list:
            for albumCard in currentGroup_dict['album_list']:
                currentGroup_dict['gridLayout'].removeWidget(albumCard)
        self.column_num = new_column
        self.__updateGridLayout()

    def __removeOldWidget(self):
        """ 从布局中移除小部件,同时设置新的布局 """
        # 将专辑卡从布局中移除
        for currentGroup_dict in self.currentGroupDict_list:
            for albumCard in currentGroup_dict['album_list']:
                currentGroup_dict['gridLayout'].removeWidget(albumCard)
            # 删除groupBox和布局
            currentGroup_dict['group'].deleteLater()
            currentGroup_dict['gridLayout'].deleteLater()

        # 先移除albumView_h_layout的当前分组
        self.albumView_hLayout.removeItem(self.albumView_hLayout_cLayout)
        # 创建一个新的竖直布局再将其加到布局中
        self.v_layout = QVBoxLayout()
        self.albumView_hLayout_cLayout = self.v_layout
        self.albumView_hLayout_cLayout.setContentsMargins(10, 0, 0, 0)

    def __addGroupToLayout(self):
        """ 将当前的分组添加到箱式布局中 """
        for index, currentGroup_dict in enumerate(self.currentGroupDict_list):
            gridLayout = currentGroup_dict['gridLayout']  # type:QGridLayout
            # 设置网格的行距
            gridLayout.setVerticalSpacing(20)
            gridLayout.setHorizontalSpacing(10)
            gridLayout.setContentsMargins(0, 0, 0, 0)
            self.v_layout.addWidget(currentGroup_dict['group'])
            if index < len(self.currentGroupDict_list)-1:
                self.v_layout.addSpacing(10)
        self.albumView_hLayout.addLayout(self.v_layout)

    def sortByAddTimeGroup(self):
        """ 按照添加时间分组 """
        # 创建一个包含所有歌曲卡的网格布局
        gridLayout = QGridLayout()
        gridLayout.setVerticalSpacing(20)
        gridLayout.setHorizontalSpacing(10)
        # 移除旧的布局
        if self.sortMode != '添加时间':
            self.sortMode = '添加时间'
            # 将组合框从布局中移除
            for currentGroup_dict in self.currentGroupDict_list:
                self.albumView_hLayout_cLayout.removeWidget(
                    currentGroup_dict['group'])
                # 删除groupBox和布局
                currentGroup_dict['group'].deleteLater()
                currentGroup_dict['gridLayout'].deleteLater()
            # 移除旧布局
            self.albumView_hLayout.removeItem(self.albumView_hLayout_cLayout)
            self.update()

        self.albumView_hLayout_cLayout = gridLayout
        self.albumView_hLayout_cLayout.setContentsMargins(10, 0, 0, 0)
        # 构造一个包含布局和小部件列表字典的列表
        self.addTimeGroup_list = [
            {'gridLayout': gridLayout, 'album_list': self.albumCard_list, 'group': QGroupBox()}]
        # 创建一个对当前分组列表引用的列表
        self.currentGroupDict_list = self.addTimeGroup_list
        # 更新网格
        self.__updateGridLayout()
        # self.__updateGridLayout()
        # 更新布局
        self.albumView_hLayout.addLayout(gridLayout)

    def sortByFirstLetter(self):
        """ 按照专辑名的首字母进行分组排序 """
        self.sortMode = 'A到Z'
        # 将专辑卡从旧布局中移除
        self.__removeOldWidget()
        # 创建分组
        firstLetter_list = []
        self.firsetLetterGroupDict_list = []
        # 将专辑卡添加到分组中
        for albumCard_dict in self.albumCardDict_list:
            # 获取专辑卡的专辑名首字母(有可能不是字母)
            firstLetter = albumCard_dict['firstLetter']
            firstLetter = firstLetter if 65 <= ord(
                firstLetter) <= 90 else '...'
            # 如果首字母属于不在列表中就将创建分组(仅限于A-Z和...)
            if firstLetter not in firstLetter_list:
                # firstLetter_list的首字母顺序和firsetLetterGroupDict_list保持一致
                firstLetter_list.append(firstLetter)
                group = GroupBox(firstLetter)
                gridLayout = QGridLayout()
                group.setLayout(gridLayout)
                self.firsetLetterGroupDict_list.append(
                    {'group': group, 'firstLetter': firstLetter,
                     'gridLayout': gridLayout, 'album_list': []})
            # 将专辑卡添加到分组中
            index = firstLetter_list.index(firstLetter)
            self.firsetLetterGroupDict_list[index]['album_list'].append(
                albumCard_dict['albumCard'])
        # 排序列表
        self.firsetLetterGroupDict_list.sort(
            key=lambda item: item['firstLetter'])
        # 将...分组移到最后
        if '...' in firstLetter_list:
            unique_group = self.firsetLetterGroupDict_list.pop(0)
            self.firsetLetterGroupDict_list.append(unique_group)
        # 将专辑加到分组的网格布局中
        self.currentGroupDict_list = self.firsetLetterGroupDict_list
        self.__updateGridLayout()
        self.__addGroupToLayout()

    def sortByYear(self):
        """ 按照专辑的年份进行分组排序 """
        self.sortMode = '发行年份'
        # 将专辑卡从旧布局中移除
        self.__removeOldWidget()
        # 创建分组
        year_list = []
        self.yearGroupDict_list = []
        # 将专辑加到分组中
        for albumCard_dict in self.albumCardDict_list:
            year = albumCard_dict['year']
            year = '未知' if year == '未知年份' else year
            # 如果年份不在年份列表中就创建分组
            if year not in year_list:
                year_list.append(year)
                # 实例化分组和网格布局
                group = GroupBox(year)
                gridLayout = QGridLayout()
                group.setLayout(gridLayout)
                self.yearGroupDict_list.append(
                    {'group': group, 'year': year,
                     'gridLayout': gridLayout, 'album_list': []})
            # 将专辑卡添加到分组中
            index = year_list.index(year)
            self.yearGroupDict_list[index]['album_list'].append(
                albumCard_dict['albumCard'])
        # 按照年份从进到远排序
        self.yearGroupDict_list.sort(
            key=lambda item: item['year'], reverse=True)
        # 检测是否含有未知分组,有的话将其移到最后一个
        if '未知' in year_list:
            unique_group = self.yearGroupDict_list.pop(0)
            self.yearGroupDict_list.append(unique_group)
        # 将专辑加到分组的网格布局中
        self.currentGroupDict_list = self.yearGroupDict_list
        self.__updateGridLayout()
        self.__addGroupToLayout()

    def sortBySonger(self):
        """ 按照专辑的专辑进行分组排序 """
        self.sortMode = '歌手'
        # 将专辑卡从旧布局中移除
        self.__removeOldWidget()
        # 创建列表
        songer_list = []
        self.songerGroupDict_list = []
        # 将专辑加到分组中
        for albumCard_dict in self.albumCardDict_list:
            songer = albumCard_dict['songer']
            if songer not in songer_list:
                songer_list.append(songer)
                group = GroupBox(songer)
                gridLayout = QGridLayout()
                group.setLayout(gridLayout)
                self.songerGroupDict_list.append(
                    {'group': group, 'songer': songer,
                     'gridLayout': gridLayout, 'album_list': []})
            # 将专辑卡添加到分组中
            index = songer_list.index(songer)
            self.songerGroupDict_list[index]['album_list'].append(
                albumCard_dict['albumCard'])
        # 排序列表
        self.songerGroupDict_list.sort(key=lambda item: item['songer'].lower())
        # 将专辑加到分组的网格布局中
        self.currentGroupDict_list = self.songerGroupDict_list
        self.__updateGridLayout()
        self.__addGroupToLayout()

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumCardViewer.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def findAlbumCardByAlbumInfo(self, albumInfo: dict) -> AlbumCard:
        """ 通过albumInfo获取对AlbumCard实例的引用 """
        for albumCard in self.albumCard_list:
            if albumCard.albumInfo == albumInfo:
                return albumCard
        return None

    def findAlbumCardByName(self, albumName: str, songerName: str) -> AlbumCard:
        """ 通过名字查找专辑卡 """
        for albumCard in self.albumCard_list:
            if albumCard.albumInfo['album'] == albumName:
                # 如果歌手名也相同就直接返回，否则在歌曲列表中寻找
                if albumCard.albumInfo['songer'] == songerName:
                    return albumCard
                else:
                    for songInfo in albumCard.albumInfo['songInfo_list']:
                        if songInfo['songer'] == songerName:
                            return albumCard
        return None

    def __albumCardCheckedStateChangedSlot(self, albumCard: AlbumCard, isChecked: bool):
        """ 专辑卡选中状态改变对应的槽函数 """
        # 如果专辑信息不在选中的专辑信息列表中且对应的专辑卡变为选中状态就将专辑信息添加到列表中
        if albumCard not in self.checkedAlbumCard_list and isChecked:
            self.checkedAlbumCard_list.append(albumCard)
            self.checkedAlbumCardNumChanged.emit(
                len(self.checkedAlbumCard_list))
        # 如果专辑信息已经在列表中且该专辑卡变为非选中状态就弹出该专辑信息
        elif albumCard in self.checkedAlbumCard_list and not isChecked:
            self.checkedAlbumCard_list.pop(
                self.checkedAlbumCard_list.index(albumCard))
            self.checkedAlbumCardNumChanged.emit(
                len(self.checkedAlbumCard_list))
        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            # 所有专辑卡进入选择模式
            self.__setAllAlbumCardSelectionModeOpen(True)
            # 发送信号要求主窗口隐藏播放栏
            self.selectionModeStateChanged.emit(True)
            # 更新标志位
            self.isInSelectionMode = True
        else:
            if not self.checkedAlbumCard_list:
                # 所有专辑卡退出选择模式
                self.__setAllAlbumCardSelectionModeOpen(False)
                # 发送信号要求主窗口显示播放栏
                self.selectionModeStateChanged.emit(False)
                # 更新标志位
                self.isInSelectionMode = False

    def __setAllAlbumCardSelectionModeOpen(self, isOpenSelectionMode: bool):
        """ 设置所有专辑卡是否进入选择模式 """
        for albumCard in self.albumCard_list:
            albumCard.setSelectionModeOpen(isOpenSelectionMode)
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
        for albumCard in self.albumCard_list:
            albumCard.checkBox.hide()

    def unCheckAlbumCards(self):
        """ 取消所有已处于选中状态的专辑卡的选中状态 """
        checkedAlbumCard_list_copy = self.checkedAlbumCard_list.copy()
        for albumCard in checkedAlbumCard_list_copy:
            albumCard.setChecked(False)

    def setAllAlbumCardCheckedState(self, isAllChecked: bool):
        """ 设置所有的专辑卡checked状态 """
        if self.isAllAlbumCardsChecked == isAllChecked:
            return
        self.isAllAlbumCardsChecked = isAllChecked
        for albumCard in self.albumCard_list:
            albumCard.setChecked(isAllChecked)

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ 显示磨砂背景 """
        # 将全局坐标转为窗口坐标
        pos = self.albumViewWidget.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 31, pos.y() - 16)
        self.albumBlurBackground.show()

    def updateOneAlbumCardSongInfo(self, newSongInfo: dict):
        """ 更新一个专辑卡的一首歌的信息 """
        for albumCard in self.albumCard_list:
            albumInfo = albumCard.albumInfo
            if albumInfo['album'] == newSongInfo['album'][0] and albumInfo['songer'] == newSongInfo['songer']:
                for i, songInfo in enumerate(albumInfo['songInfo_list']):
                    if songInfo['songPath'] == newSongInfo['songPath']:
                        albumInfo['songInfo_list'][i] = newSongInfo.copy()
                        return albumInfo
        return {}
