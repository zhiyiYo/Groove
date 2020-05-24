import json
import os
import re
import sys

import pinyin
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBitmap, QImage, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QScrollArea,
    QVBoxLayout, QWidget)

import get_album_cover
from album_card import AlbumCard
from get_album_info import AlbumInfo


class AlbumCardViewer(QWidget):
    """ 定义一个专辑卡视图 """

    def __init__(self, target_path, parent=None):
        super().__init__(parent)

        # 初始化网格的列数
        self.column_num = 5
        self.total_row_num = 0

        # 设置当前排序方式
        self.sortMode = '添加时间'

        # 先扫描本地音乐的专辑封面
        self.getAlbumCover = get_album_cover.AlbumCover(target_path)
        # 获取专辑信息
        self.albumInfo = AlbumInfo()

        # 实例化布局
        self.gridLayout = QGridLayout()
        self.albumView_h_layout = QHBoxLayout()
        self.all_h_layout = QHBoxLayout()

        # 实例化滚动区域和滚动区域的窗口
        self.scrollArea = QScrollArea(self)
        self.albumView = QWidget()

        # 初始化小部件
        self.initWidget()
        # 创建专辑卡并将其添加到布局中
        self.createAlbumCards()
        self.initLayout()

        # 设置样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(1267, 638)
        self.scrollArea.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.verticalScrollBar().setSingleStep(30)

    def createAlbumCards(self):
        """ 将专辑卡添加到窗口中 """
        self.albumCardDict_list = []
        self.albumCard_list = []
        for albumInfo_dict in self.albumInfo.albumInfo_list:
            # 实例化专辑卡
            albumCard = AlbumCard(albumInfo_dict, self)
            album = albumInfo_dict['album']
            # 将含有专辑卡及其信息的字典插入列表
            self.albumCard_list.append(albumCard)
            self.albumCardDict_list.append({'albumCard': albumCard,
                                            'albumName': album,
                                            'year': albumInfo_dict['year'],
                                            'songer': albumInfo_dict['songer'],
                                            'firstLetter': pinyin.get_initial(album)[0].upper()})

    def initLayout(self):
        """ 初始化布局 """
        # 引用albumView_h_layout当前的布局
        self.album_h_layout_clayout = self.gridLayout
        # 创建添加时间分组
        self.createAddTimeGroup()
        self.updateGridLayout()
        self.gridLayout.setVerticalSpacing(11)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.albumView_h_layout.setContentsMargins(0, 0, 0, 0)

        self.albumView.setLayout(self.albumView_h_layout)
        self.scrollArea.setWidget(self.albumView)
        # 设置全局布局
        self.all_h_layout.addWidget(self.scrollArea)
        self.setLayout(self.all_h_layout)

    def updateGridLayout(self):
        """ 更新网格 """
        self.total_row_num = 0
        self.vertical_spacing_count = len(self.currentGroupDict_list)-1
        for currentGroup_dict in self.currentGroupDict_list:
            columns = range(self.column_num)
            rows = range(
                (len(currentGroup_dict['album_list']) - 1) // self.column_num + 1)
            # 引用当前分组的网格布局
            gridLayout = currentGroup_dict['gridLayout']

            # 设置网格大小
            for column in columns:
                gridLayout.setColumnMinimumWidth(
                    column, 221)
            for row in rows:
                gridLayout.setRowMinimumHeight(
                    row, 292)
            for index, albumCard in enumerate(currentGroup_dict['album_list']):
                x = index // self.column_num
                y = index-self.column_num*x
                gridLayout.addWidget(
                    albumCard, x, y, 1, 1)
            # 获取当前的总行数
            self.current_row_num = x + 1
            self.total_row_num += self.current_row_num
            # 如果专辑数小于设定的列数，就在右侧增加弹簧
            offset = self.column_num - len(self.albumCardDict_list)
            for i in range(offset):
                gridLayout.setColumnStretch(i + offset - 1, 1)

            # 如果现在的总行数小于网格的总行数，就将多出来的行宽度的最小值设为0
            for i in range(gridLayout.rowCount() - 1, self.current_row_num - 1, -1):
                gridLayout.setRowMinimumHeight(i, 0)

            # 如果现在的总列数小于网格的总列数，就将多出来的列的宽度的最小值设置为0
            for i in range(gridLayout.columnCount() - 1, self.column_num - 1, -1):
                gridLayout.setColumnMinimumWidth(i, 0)

        self.albumView.setFixedWidth(221 * self.column_num)
        self.albumView.setFixedHeight(
            313 * self.total_row_num+10*self.vertical_spacing_count)

    def resizeEvent(self, event):
        """ 根据宽度调整网格的列数 """
        # 如果第一次超过1337就调整网格的列数
        if self.width() >= 1353 and self.column_num != 6:
            for albumCard_dict in self.albumCardDict_list:
                self.gridLayout.removeWidget(albumCard_dict['albumCard'])
            self.column_num = 6
            self.updateGridLayout()
        elif 1134 < self.width() < 1353 and self.column_num != 5:
            for albumCard_dict in self.albumCardDict_list:
                self.gridLayout.removeWidget(albumCard_dict['albumCard'])
            self.column_num = 5
            self.updateGridLayout()
        elif self.width() <= 1134:
            for albumCard_dict in self.albumCardDict_list:
                self.gridLayout.removeWidget(albumCard_dict['albumCard'])
            self.column_num = 4
            self.updateGridLayout()

    def createAddTimeGroup(self):
        """ 按照添加时间分组 """

        # 移除旧的布局
        if self.sortMode != '添加时间':
            self.sortMode = '添加时间'
            # 将组合框从布局中移除
            for currentGroup_dict in self.currentGroupDict_list:
                self.album_h_layout_clayout.removeWidget(
                    currentGroup_dict['group'])
                # 删除groupBox和布局
                currentGroup_dict['group'].deleteLater()
                currentGroup_dict['gridLayout'].deleteLater()
            # 移除旧布局
            self.albumView_h_layout.removeItem(self.album_h_layout_clayout)
            self.update()

        self.album_h_layout_clayout = self.gridLayout
        # 构造一个包含布局和小部件列表字典的列表
        self.addTimeGroup_list = [
            {'gridLayout': self.gridLayout, 'album_list': self.albumCard_list}]
        # 创建一个对当前分组列表引用的列表
        self.currentGroupDict_list = self.addTimeGroup_list
        # 更新网格
        self.updateGridLayout()
        # 更新布局
        self.albumView_h_layout.addLayout(self.gridLayout)

    def createFirstLetterGroup(self):
        """ 按照首字母对歌手进行分组 """
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
        # 将专辑卡从布局中移除
        for currentGroup_dict in self.currentGroupDict_list:
            for albumCard in currentGroup_dict['album_list']:
                currentGroup_dict['gridLayout'].removeWidget(albumCard)
        # 先移除albumView_h_layout的当前分组
        self.albumView_h_layout.removeItem(self.album_h_layout_clayout)
        # 创建一个新的竖直布局再将其加到布局中
        self.v_layout = QVBoxLayout()
        self.album_h_layout_clayout = self.v_layout

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
                firstLetterGroup_dict['firstLetter'] = '...'

        # 将专辑加到分组的网格布局中
        self.currentGroupDict_list = self.firsetLetterGroupDict_list
        self.updateGridLayout()
        for index, firstLetterGroup_dict in enumerate(self.firsetLetterGroupDict_list):
            gridLayout = firstLetterGroup_dict['gridLayout']
            # 设置网格的行距
            gridLayout.setVerticalSpacing(20)
            gridLayout.setContentsMargins(0, 0, 0, 0)
            self.v_layout.addWidget(firstLetterGroup_dict['group'])
            if index < len(self.firsetLetterGroupDict_list)-1:
                self.v_layout.addSpacing(10)

        self.albumView_h_layout.addLayout(self.v_layout)

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumCardViewer.qss', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = AlbumCardViewer('D:\\KuGou')
    demo.show()
    sys.exit(app.exec_())
