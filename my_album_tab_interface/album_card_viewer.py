import json
import os
import re
import sys
from time import time

import pinyin
from PyQt5.QtCore import QEvent, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QScrollArea,
    QVBoxLayout, QWidget)

from get_info.get_album_cover import GetAlbumCover
from get_info.get_album_info import AlbumInfo
from my_album_tab_interface.album_card import AlbumCard
from my_widget.album_blur_background import AlbumBlurBackground
from my_widget.my_scrollArea import ScrollArea
from my_widget.my_toolTip import ToolTip


class AlbumCardViewer(QWidget):
    """ 定义一个专辑卡视图 """
    columnChanged = pyqtSignal()
    playSignal = pyqtSignal(list)
    nextPlaySignal = pyqtSignal(list)
    addAlbumToPlaylistSignal = pyqtSignal(list)
    switchToAlbumInterfaceSig = pyqtSignal(dict)
    
    def __init__(self, target_path_list:list, parent=None):
        super().__init__(parent)
        # 初始化网格的列数
        self.column_num = 5
        self.total_row_num = 0
        # 设置专辑为空标志位
        self.isAlbumEmpty = False
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
        # 初始化小部件
        self.__initWidget()
        # 创建专辑卡并将其添加到布局中
        self.__createAlbumCards()
        self.initLayout()
        self.__connectSignalToSlot()
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

    def __createAlbumCards(self):
        """ 将专辑卡添加到窗口中 """
        self.albumCardDict_list = []
        self.albumCard_list = []
        for albumInfo_dict in self.albumInfo.albumInfo_list:
            # 实例化专辑卡
            albumCard = AlbumCard(albumInfo_dict, self, self.albumViewWidget)
            album = albumInfo_dict['album']
            # 将含有专辑卡及其信息的字典插入列表
            self.albumCard_list.append(albumCard)
            self.albumCardDict_list.append({'albumCard': albumCard,
                                            'albumName': album,
                                            'year': albumInfo_dict['year'][:4],
                                            'songer': albumInfo_dict['songer'],
                                            'firstLetter': pinyin.get_initial(album[0])[0].upper()})

    def __connectSignalToSlot(self):
        """ 将信号连接到槽函数 """
        for albumCard in self.albumCard_list:
            # 播放
            albumCard.playSignal.connect(
                lambda playlist: self.playSignal.emit(playlist))
            # 下一首播放
            albumCard.nextPlaySignal.connect(
                lambda playlist: self.nextPlaySignal.emit(playlist))
            # 添加到播放列表
            albumCard.addToPlaylistSignal.connect(
                lambda playlist: self.addAlbumToPlaylistSignal.emit(playlist))
            # 进入专辑界面
            albumCard.switchToAlbumInterfaceSig.connect(
                lambda albumInfo: self.switchToAlbumInterfaceSig.emit(albumInfo))

    def initLayout(self):
        """ 初始化布局 """
        # 如果没有专辑，就置位专辑为空标志位并直接返回
        if not self.albumCard_list:
            self.isAlbumEmpty = True
            self.hide()
            return
        # 创建添加时间分组
        self.sortByAddTimeGroup()
        self.__updateGridLayout()
        self.gridLayout.setVerticalSpacing(11)
        self.gridLayout.setHorizontalSpacing(0)
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
            if gridIndex!=len(self.currentGroupDict_list)-1:
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
                    column, 221)
            for row in rows:
                if row!=max(rows):
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
                        gridLayout.addWidget(albumCard, x, y, 2, 1,Qt.AlignTop)
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
            gridLayout = currentGroup_dict['gridLayout']
            # 设置网格的行距
            gridLayout.setVerticalSpacing(20)
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
            group = QGroupBox(letter)
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
            group = QGroupBox(year)
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
            group = QGroupBox(songer)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = AlbumCardViewer(['D:\\KuGou\\'])
    demo.show()
    sys.exit(app.exec_())
