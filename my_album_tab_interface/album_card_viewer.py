# coding:utf-8

import re
from time import time

import pinyin
from PyQt5.QtCore import (QEvent, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, pyqtSignal)
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QScrollArea,
    QVBoxLayout, QWidget)

from get_info.get_album_cover import GetAlbumCover
from get_info.get_album_info import AlbumInfo
from my_album_tab_interface.album_card import AlbumCard
from my_widget.album_blur_background import AlbumBlurBackground
from my_widget.my_groupBox import GroupBox
from my_widget.my_scrollArea import ScrollArea
from my_widget.my_toolTip import ToolTip


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

    def __init__(self, target_path_list: list, parent=None):
        super().__init__(parent)
        # 初始化网格的列数
        self.column_num = 5
        self.total_row_num = 0
        self.albumCardDict_list = []
        self.albumCard_list = []
        self.checkedAlbumCard_list = []
        # 初始化标志位
        self.isAlbumEmpty = False
        self.isInSelectionMode = False
        self.isAllAlbumCardsChecked=False
        # 设置当前排序方式
        self.sortMode = '添加时间'
        # 先扫描本地音乐的专辑封面
        self.getAlbumCover = GetAlbumCover(target_path_list)
        # 获取专辑信息
        self.albumInfo = AlbumInfo()
        # 实例化布局
        self.albumView_hLayout = QHBoxLayout()
        self.all_h_layout = QHBoxLayout()
        # 实例化滚动区域和滚动区域的窗口
        self.scrollArea = ScrollArea(self)
        self.albumViewWidget = QWidget()
        self.albumViewWidget.albumBlurBackground = AlbumBlurBackground(
            self.albumViewWidget)
        # 实例化并引用提示条
        """ self.albumViewWidget.customToolTip = ToolTip(parent=self.albumViewWidget)
        self.customToolTip = self.albumViewWidget.customToolTip """
        # 创建专辑卡并将其添加到布局中
        self.__createAlbumCards()
        # 初始化小部件
        self.__initWidget()
        self.__initLayout()
        # 设置样式
        self.__setQss()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1270, 760)
        # 初始化滚动条
        self.scrollArea.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        # 隐藏磨砂背景
        self.albumViewWidget.albumBlurBackground.hide()
        # 分配ID
        self.setObjectName('father')
        self.albumViewWidget.setObjectName('albumViewWidget')
        # 信号连接到槽
        self.__connectSignalToSlot()

    def __createAlbumCards(self):
        """ 将专辑卡添加到窗口中 """
        # 创建并行动画组
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAni_list = []
        for albumInfo_dict in self.albumInfo.albumInfo_list:
            # 实例化专辑卡和动画
            albumCard = AlbumCard(albumInfo_dict, self, self.albumViewWidget)
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
            albumCard.checkedStateChanged.connect(self.__albumCardCheckedStateChanedSlot)
            # albumCard.updateAlbumInfoSig.connect(self.__updateAlbumInfoSlot)

    def __initLayout(self):
        """ 初始化布局 """
        # 如果没有专辑，就置位专辑为空标志位并直接返回
        if not self.albumCard_list:
            self.isAlbumEmpty = True
            self.hide()
            return
        # 创建添加时间分组
        self.sortByAddTimeGroup()
        self.__updateGridLayout()
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.albumView_hLayout.setContentsMargins(0, 0, 0, 0)

        self.albumViewWidget.setLayout(self.albumView_hLayout)
        self.scrollArea.setWidget(self.albumViewWidget)
        # 设置全局布局
        self.all_h_layout.addWidget(self.scrollArea)
        self.all_h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.all_h_layout)

    def __updateGridLayout(self):
        """ 更新网格 """
        self.total_row_num = 0
        self.vertical_spacing_count = len(self.currentGroupDict_list)-1
        for currentGroup_dict in self.currentGroupDict_list:
            # 引用当前分组的网格布局
            gridLayout = currentGroup_dict['gridLayout']  # type:QGridLayout
            gridIndex = self.currentGroupDict_list.index(currentGroup_dict)
            columns = range(self.column_num)
            if gridIndex != len(self.currentGroupDict_list)-1:
                rows = range(
                    (len(currentGroup_dict['album_list']) - 1) // self.column_num + 1)
            else:
                # 补上底部播放栏所占的位置
                rows = range(
                    (len(currentGroup_dict['album_list']) - 1) // self.column_num + 2)
            self.current_row_num = max(rows) + 1
            # 设置网格大小
            for column in columns:
                gridLayout.setColumnMinimumWidth(
                    column, 211)
            for row in rows:
                if row != max(rows):
                    gridLayout.setRowMinimumHeight(
                        row, 292)
                else:
                    if gridIndex != len(self.currentGroupDict_list) - 1:
                        gridLayout.setRowMinimumHeight(
                            row, 292)
                    else:
                        gridLayout.setRowMinimumHeight(
                            row, 146)
            for index, albumCard in enumerate(currentGroup_dict['album_list']):
                x = index // self.column_num
                y = index - self.column_num * x
                if x != max(rows) - 1:
                    gridLayout.addWidget(albumCard, x, y, 1, 1)
                else:
                    if gridIndex == len(self.currentGroupDict_list) - 1:
                        gridLayout.addWidget(
                            albumCard, x, y, 2, 1, Qt.AlignTop)
                    else:
                        gridLayout.addWidget(albumCard, x, y, 1, 1)

            # 获取当前的总行数
            self.total_row_num += self.current_row_num
            # 如果专辑数小于设定的列数，就在右侧增加弹簧
            """ offset = self.column_num - len(self.albumCardDict_list)
            for i in range(offset):
                gridLayout.setColumnStretch(i + offset - 1, 1) """

            # 如果现在的总行数小于网格的总行数，就将多出来的行宽度的最小值设为0
            for i in range(gridLayout.rowCount() - 1, self.current_row_num - 1, -1):
                gridLayout.setRowMinimumHeight(i, 0)

            # 如果现在的总列数小于网格的总列数，就将多出来的列的宽度的最小值设置为0
            for i in range(gridLayout.columnCount() - 1, self.column_num - 1, -1):
                gridLayout.setColumnMinimumWidth(i, 0)

        self.albumViewWidget.setFixedWidth(221 * self.column_num)
        if self.sortMode == '添加时间':
            self.albumViewWidget.setFixedHeight(303*self.total_row_num)
        else:
            # 补上分组标题所占的高度
            self.albumViewWidget.setFixedHeight(
                303 * self.total_row_num + 34 * len(self.currentGroupDict_list))

    def resizeEvent(self, event):
        """ 根据宽度调整网格的列数 """
        super().resizeEvent(event)
        # 如果第一次超过1337就调整网格的列数
        if self.width() >= 1335 and self.column_num != 6:
            self.__updateColumnNum(6)
        elif 1115 < self.width() < 1335 and self.column_num != 5:
            self.__updateColumnNum(5)
        elif 895 < self.width() <= 1115 and self.column_num != 4:
            self.__updateColumnNum(4)
        elif 675 < self.width() <= 895:
            self.__updateColumnNum(3)
        elif self.width() <= 675:
            self.__updateColumnNum(2)

    def __updateColumnNum(self, new_column):
        """ 更新网格列数 """
        for currentGroup_dict in self.currentGroupDict_list:
            for albumCard in currentGroup_dict['album_list']:
                currentGroup_dict['gridLayout'].removeWidget(albumCard)
        self.column_num = new_column
        self.__updateGridLayout()
        # 发送更新列数信号
        self.columnChanged.emit()

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
        self.gridLayout = QGridLayout()
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

        self.albumView_hLayout_cLayout = self.gridLayout
        # 构造一个包含布局和小部件列表字典的列表
        self.addTimeGroup_list = [
            {'gridLayout': self.gridLayout, 'album_list': self.albumCard_list, 'group': QGroupBox()}]
        # 创建一个对当前分组列表引用的列表
        self.currentGroupDict_list = self.addTimeGroup_list
        # 更新网格
        self.__updateGridLayout()
        # 更新布局
        self.albumView_hLayout.addLayout(self.gridLayout)

    def __createFirstLetterGroup(self):
        """ 按照首字母对专辑创建分组 """
        # 获取专辑的第一个字符组成的集合
        first_char_set = {albumInfo_dict['albumName'][0]
                          for albumInfo_dict in self.albumCardDict_list}
        # 获取第一个字符的大写首字母
        first_letter_set = {pinyin.get_initial(
            first_char)[0].upper() for first_char in first_char_set}

        first_letter_set_copy = first_letter_set.copy()
        for letter in first_letter_set_copy:
            # 匹配英文字母
            Match = re.match(r'[A-Z]', letter)
            if not Match:
                first_letter_set.remove(letter)
                first_letter_set.add('...')

        # 创建分组
        self.firsetLetterGroupDict_list = []
        for letter in first_letter_set:
            # 实例化分组和网格布局
            group = GroupBox(letter)
            gridLayout = QGridLayout()
            group.setLayout(gridLayout)
            # 将含有字母和分组的字典插入列表
            self.firsetLetterGroupDict_list.append(
                {'group': group, 'letter': letter, 'gridLayout': gridLayout, 'album_list': []})

        # 按照字母排序列表
        self.firsetLetterGroupDict_list.sort(key=lambda item: item['letter'])

        # 检测是否含有...分组,有的话将其移到最后一个
        if self.firsetLetterGroupDict_list[0]['letter'] == '...':
            unique_group = self.firsetLetterGroupDict_list.pop(0)
            self.firsetLetterGroupDict_list.append(unique_group)

    def sortByFirsetLetter(self):
        """ 按照专辑名的首字母进行分组排序 """
        self.__createFirstLetterGroup()
        # 将专辑卡从旧布局中移除
        self.__removeOldWidget()

        # 将专辑加到分组中
        for albumCard_dict in self.albumCardDict_list:
            for firstLetterGroup_dict in self.firsetLetterGroupDict_list:
                if firstLetterGroup_dict['letter'] == albumCard_dict['firstLetter']:
                    firstLetterGroup_dict['album_list'].append(
                        albumCard_dict['albumCard'])
                    break
            else:
                # 将不符合分组依据的头像插到特殊分组中
                self.firsetLetterGroupDict_list[-1]['album_list'].append(
                    albumCard_dict['albumCard'])
                #firstLetterGroup_dict['firstLetter'] = '...'

        # 将专辑加到分组的网格布局中
        self.currentGroupDict_list = self.firsetLetterGroupDict_list
        self.__updateGridLayout()
        self.__addGroupToLayout()

    def __createYearGroup(self):
        """ 对专辑按照年份创建分组 """
        # 获取专辑的年份组成的集合
        year_set = {albumInfo_dict['year']
                    for albumInfo_dict in self.albumCardDict_list}

        # 将未知年份替换为未知
        if '未知年份' in year_set:
            year_set.remove('未知年份')
            year_set.add('未知')

        # 创建分组
        self.yearGroupDict_list = []
        for year in year_set:
            # 实例化分组和网格布局
            group = GroupBox(year)
            gridLayout = QGridLayout()
            group.setLayout(gridLayout)
            # 将含有字母和分组的字典插入列表
            self.yearGroupDict_list.append(
                {'group': group, 'year': year, 'gridLayout': gridLayout, 'album_list': []})

        # 按照年份从进到远排序
        self.yearGroupDict_list.sort(
            key=lambda item: item['year'], reverse=True)

        # 检测是否含有未知分组,有的话将其移到最后一个
        if self.yearGroupDict_list[0]['year'] == '未知':
            unique_group = self.yearGroupDict_list.pop(0)
            self.yearGroupDict_list.append(unique_group)

    def sortByYear(self):
        """ 按照专辑的年份进行分组排序 """
        self.__createYearGroup()
        # 将专辑卡从旧布局中移除
        self.__removeOldWidget()
        # 将专辑加到分组中
        for albumCard_dict in self.albumCardDict_list:
            for yearGroup_dict in self.yearGroupDict_list:
                if yearGroup_dict['year'] == albumCard_dict['year']:
                    yearGroup_dict['album_list'].append(
                        albumCard_dict['albumCard'])
                    break
            else:
                # 将不符合分组依据的头像插到特殊分组中
                self.yearGroupDict_list[-1]['album_list'].append(
                    albumCard_dict['albumCard'])

        # 将专辑加到分组的网格布局中
        self.currentGroupDict_list = self.yearGroupDict_list
        self.__updateGridLayout()
        self.__addGroupToLayout()

    def __createSongerGroup(self):
        """ 对专辑的所属歌手创建分组 """
        songer_set = {albumInfo_dict['songer']
                      for albumInfo_dict in self.albumCardDict_list}
        # 创建分组
        self.songerGroupDict_list = []
        for songer in songer_set:
            # 实例化分组和网格布局
            group = GroupBox(songer)
            gridLayout = QGridLayout()
            group.setLayout(gridLayout)
            # 将含有字母和分组的字典插入列表
            self.songerGroupDict_list.append(
                {'group': group, 'songer': songer, 'gridLayout': gridLayout, 'album_list': []})

        # 按照年份从进到远排序
        self.songerGroupDict_list.sort(key=lambda item: item['songer'].lower())

    def sortBySonger(self):
        """ 按照专辑的专辑进行分组排序 """
        self.__createSongerGroup()
        # 将专辑卡从旧布局中移除
        self.__removeOldWidget()
        # 将专辑加到分组中
        for albumCard_dict in self.albumCardDict_list:
            for songerGroup_dict in self.songerGroupDict_list:
                if songerGroup_dict['songer'] == albumCard_dict['songer']:
                    songerGroup_dict['album_list'].append(
                        albumCard_dict['albumCard'])
                    break

        # 将专辑加到分组的网格布局中
        self.currentGroupDict_list = self.songerGroupDict_list
        self.__updateGridLayout()
        self.__addGroupToLayout()

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumCardViewer.qss', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

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

    def __updateAlbumInfoSlot(self, oldAlbumInfo: dict, newAlbumInfo: dict):
        """ 更新专辑列表的专辑信息 """
        if oldAlbumInfo in self.albumInfo.albumInfo_list:
            index = self.albumInfo.albumInfo_list.index(oldAlbumInfo)
            self.albumInfo.albumInfo_list[index] = newAlbumInfo
            print('更新专辑列表信息')
        else:
            print('没找到旧专辑信息')
        print('==' * 40)

    def __albumCardCheckedStateChanedSlot(self, albumCard:AlbumCard, isChecked: bool):
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
