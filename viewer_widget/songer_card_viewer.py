import json
import sys
import re
import os
import pinyin
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBitmap, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QScrollArea,
    QScrollBar, QVBoxLayout, QWidget)

sys.path.append('..')
from Groove.card_widget.songer_card import SongerCard
from Groove.my_widget.my_scrollArea import ScrollArea


class SongerCardViewer(QWidget):
    """ 创建一个包含所有歌手头像的界面 """

    def __init__(self,parent=None):
        super().__init__(parent)

        self.resize(1267, 781-23)
        # 设置网格列数
        self.column_num = 5
        self.total_cow_num = 0
        # 实例化一个滚动区域
        self.scrollArea = ScrollArea(self)
        self.songerViewWidget = QWidget()
        # 实例化标题栏
        #self.firstLetterLabel = QLabel('A', self)
        # 实例化布局
        self.all_h_layout = QHBoxLayout()
        self.gridLayout = QGridLayout()
        self.v_layout = QVBoxLayout()
        # 初始化歌手头像和布局
        self.createSongerHeadPortraits()
        self.createSongerGroup()
        self.addSongerToGroup()
        self.initLayout()
        self.initWidget()
        # 设置层叠样式
        self.setQss()

    def initWidget(self):
        """ 初始化歌手头像 """
        # 隐藏滚动区域的自带滚动条
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置滚动条的步长
        self.scrollArea.verticalScrollBar().setSingleStep(40)
        # 设置标题栏的位置
        #self.firstLetterLabel.setGeometry(0, 0, self.width(), 47)
        # 分配ID
        self.setObjectName('father')
        self.songerViewWidget.setObjectName('songerViewWidget')
        # self.firstLetterLabel.setObjectName('firstLetter')

    def createSongerHeadPortraits(self):
        """ 创建歌手头像窗口列表 """
        # 从json文件中读取歌手信息
        self.songer_list=[]
        with open('Data\\songerInfo.json', encoding='utf-8') as f:
            self.songerInfo_list = json.load(f)
        with open('Data\\songInfo.json', encoding='utf-8') as f:
            self.songInfo_list = json.load(f)
            # 根据歌曲列表来选择要显示出来的歌手
            self.oldSonger_list = [songInfo_dict.get('songer') for songInfo_dict in self.songInfo_list]
            # 将合唱歌手名拆开
            for oldSonger in self.oldSonger_list:
                self.songer_list += oldSonger.split('、')

        # 排序歌手名
        self.songerInfo_list.sort(
            key=lambda info_dict: info_dict['songer'].upper())

        # 创建歌手头像列表
        self.songerHeadPortrait_dict_list = []
        self.songerInfo_list_copy=self.songerInfo_list.copy()
        for songerInfo_dict in self.songerInfo_list.copy():
            songerName = songerInfo_dict['songer']
            # 只显示有在歌曲列表中的歌手
            if songerName in self.songer_list:
                try:
                    songerPicPath = os.path.join("resource\\Songer Photos\\"+songerName,
                                                os.listdir('resource\\Songer Photos\\'+songerName)[0])
                except:
                    songerPicPath = 'resource\\Songer Photos\\未知歌手.png'
                # 实例化歌手头像窗口
                songerCard = SongerCard(songerPicPath, songerName)
                # 将包含头像窗口，歌手名，歌手名首字母的字典插入列表
                self.songerHeadPortrait_dict_list.append({'songerCard': songerCard,
                                                        'songerName': songerName,
                                                        'firstLetter': pinyin.get_initial(songerName)[0].upper()})
            else:
                # 移除不在歌曲卡中的歌手
                self.songerInfo_list.remove(songerInfo_dict)                                            

    def createSongerGroup(self):
        """ 按照首字母对歌手进行分组 """
        # 获取歌手名的第一个字符组成的集合
        
        first_char_set = {songerInfo_dict['songer'][0]
                          for songerInfo_dict in self.songerInfo_list}
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
        self.songerHeadGroup_dict_list = []
        for letter in first_letter_set:
            # 实例化分组和网格布局
            group = QGroupBox(letter)
            gridLayout = QGridLayout()
            group.setLayout(gridLayout)
            # 将含有字母和分组的字典插入列表
            self.songerHeadGroup_dict_list.append(
                {'group': group, 'letter': letter, 'gridLayout': gridLayout, 'songer_list': []})

        # 按照字母排序列表
        self.songerHeadGroup_dict_list.sort(key=lambda item: item['letter'])

        # 检测是否含有...分组,有的话将其移到最后一个
        if self.songerHeadGroup_dict_list[0]['letter'] == '...':
            unique_group = self.songerHeadGroup_dict_list.pop(0)
            self.songerHeadGroup_dict_list.append(unique_group)

    def addSongerToGroup(self):
        """ 将歌手头像添加到分组中 """
        for songerHeadPortrait_dict in self.songerHeadPortrait_dict_list:
            for songerHeadGroup_dict in self.songerHeadGroup_dict_list:
                if songerHeadGroup_dict['letter'] == songerHeadPortrait_dict['firstLetter']:
                    songerHeadGroup_dict['songer_list'].append(
                        songerHeadPortrait_dict['songerCard'])
                    break
            else:
                # 将不符合分组依据的头像插到特殊分组中
                self.songerHeadGroup_dict_list[-1]['songer_list'].append(
                    songerHeadPortrait_dict['songerCard'])

    def initLayout(self):
        """ 初始化布局 """
        self.__updateGridLayout()

        for songerHeadGroup_dict in self.songerHeadGroup_dict_list:
            gridLayout = songerHeadGroup_dict['gridLayout']
            # 设置网格的行距
            gridLayout.setVerticalSpacing(20)
            gridLayout.setContentsMargins(0, 0, 0, 0)
            self.v_layout.addWidget(songerHeadGroup_dict['group'])
            self.v_layout.addSpacing(10)

        # 设置歌手头像视图窗口的布局
        self.songerViewWidget.setLayout(self.v_layout)
        # 将歌手头像窗口添加到滚动区域中
        self.scrollArea.setWidget(self.songerViewWidget)
        # 设置全局布局
        self.all_h_layout.addWidget(self.scrollArea)
        self.all_h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.all_h_layout)

    def setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\songerCardViewer.qss', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def __updateGridLayout(self):
        """ 更新网格的列数 """
        self.total_cow_num = 0
        self.vertical_spacing_count = len(self.songerHeadPortrait_dict_list)-1
        for songerHeadGroup_dict in self.songerHeadGroup_dict_list:
            # 根据每个分组含有的歌手数量计算网格的行数和列数
            columns = range(self.column_num)
            rows = range(
                (len(songerHeadGroup_dict['songer_list']) - 1) // self.column_num + 1)
            self.current_row_num = max(rows) + 1
            self.total_cow_num += self.current_row_num

            gridLayout = songerHeadGroup_dict['gridLayout']
            # 设置网格大小
            for column in columns:
                gridLayout.setColumnMinimumWidth(
                    column, 224)
            for row in rows:
                gridLayout.setRowMinimumHeight(
                    row, 268)
            # 向网格中添加小部件
            for index, songerHeadPortrait in enumerate(songerHeadGroup_dict['songer_list']):
                x = index // self.column_num
                y = index-self.column_num*x
                gridLayout.addWidget(
                    songerHeadPortrait, x, y, 1, 1)

            # 如果现在的总行数小于网格的总行数，就将多出来的行宽度的最小值设为0
            for i in range(gridLayout.rowCount() - 1, self.current_row_num - 1, -1):
                gridLayout.setRowMinimumHeight(i, 0)
            # 如果总的列数少于网格的总列数，就将多出来列的最小宽度设置为0
            for i in range(gridLayout.columnCount() - 1, self.column_num - 1, -1):
                gridLayout.setColumnMinimumWidth(i, 0)

        # 设置窗口的最小宽度
        self.songerViewWidget.setFixedWidth(self.column_num * 224)
        self.songerViewWidget.setFixedHeight(
            284*self.total_cow_num+40*len(self.songerHeadGroup_dict_list))

    def resizeEvent(self, event):
        """ 根据宽度调整列数 """
        if self.width() >= 1337 and self.column_num != 6:
            self.__updateColumnNum(6)
        elif 1135 < self.width() < 1337 and self.column_num != 5:
            self.__updateColumnNum(5)
        elif 913 < self.width() <= 1135 and self.column_num != 4:
            self.__updateColumnNum(4)
        elif self.width() <= 913:
            self.__updateColumnNum(3)

    def __updateColumnNum(self, new_column):
        """ 移除旧的布局中的小部件并更新布局 """
        for songerHeadGroup_dict in self.songerHeadGroup_dict_list:
            for songerHeadPortrait in songerHeadGroup_dict['songer_list']:
                songerHeadGroup_dict['gridLayout'].removeWidget(
                    songerHeadPortrait)
        self.column_num = new_column
        self.__updateGridLayout()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongerCardViewer()
    demo.show()
    sys.exit(app.exec_())
