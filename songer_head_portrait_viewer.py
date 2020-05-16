import json
import sys
import re
import pinyin
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBitmap, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QScrollArea,
    QScrollBar, QVBoxLayout, QWidget)

from songer_card import SongerCard


class SongerHeadPortraitViewer(QWidget):
    """ 创建一个包含所有歌手头像的界面 """

    def __init__(self):
        super().__init__()

        self.resize(1267, 638)

        # 实例化一个滚动区域
        self.scrollArea = QScrollArea(self)
        self.songerHeadViewer = Widget()

        # 实例化标题栏
        #self.firstLetterLabel = QLabel('A', self)

        # 实例化滚动条
        #self.scrollBar = QScrollBar(self)

        # 实例化布局
        self.all_h_layout = QHBoxLayout()
        self.gridLayout = QGridLayout()
        self.v_layout = QVBoxLayout()

        # 初始化歌手头像和布局
        self.createSongerHeadPortraits()
        self.createSongerGroup()
        self.addSongerToGroup()
        self.initLayout(5)
        self.initWidget()

        # 设置层叠样式
        self.setQss()

    def initWidget(self):
        """ 初始化歌手头像 """
        # 隐藏滚动区域的自带滚动条
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #设置滚动条的步长
        self.scrollArea.verticalScrollBar().setSingleStep(40)

        # 将两个滚动条关联起来
        """ self.scrollBar.setMaximum(
            self.scrollArea.verticalScrollBar().maximum())

        self.scrollBar.valueChanged.connect(
            lambda: self.scrollArea.verticalScrollBar().setValue(self.scrollBar.value()))

        self.scrollArea.verticalScrollBar().valueChanged.connect(
            lambda: self.scrollBar.setValue(self.scrollArea.verticalScrollBar().value())) """

        # 设置标题栏的位置
        #self.firstLetterLabel.setGeometry(0, 0, self.width(), 47)

        # 分配ID
        self.setObjectName('father')
        self.songerHeadViewer.setObjectName('songerHeadViewer')
        #self.firstLetterLabel.setObjectName('firstLetter')

    def createSongerHeadPortraits(self):
        """ 创建歌手头像窗口列表 """
        # 从json文件中读取歌手信息
        with open('Data\\songerInfo.json', encoding='utf-8') as f:
            self.songerInfo_list = json.load(f)

        # 排序歌手名
        self.songerInfo_list.sort(
            key=lambda info_dict: info_dict['songer'].upper())

        # 创建歌手头像列表
        self.songerHeadPortrait_dict_list = []
        for songerInfo_dict in self.songerInfo_list:
            songerName = songerInfo_dict['songer']
            songerPicPath = 'resource\\Songer Photos\\' + \
                songerName + '\\'+songerInfo_dict['songer']+'.jpg'
            # 实例化歌手头像窗口
            songerCard = SongerCard(songerPicPath, songerName)
            # 将包含头像窗口，歌手名，歌手名首字母的字典插入列表
            self.songerHeadPortrait_dict_list.append({'index': 0,
                                                      'songerCard': songerCard,
                                                      'songerName': songerName,
                                                      'firstLetter': pinyin.get_initial(songerName)[0].upper()})

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
                songerHeadGroup_dict['firstLetter'] = '...'

    def initLayout(self, column_num):
        """ 初始化布局 """

        for songerHeadGroup_dict in self.songerHeadGroup_dict_list:
            # 根据每个分组含有的歌手数量计算网格的行数和列数
            columns = range(column_num)
            rows = range(
                (len(songerHeadGroup_dict['songer_list']) - 1) // 5 + 1)
            gridLayout = songerHeadGroup_dict['gridLayout']
            # 设置网格的行距
            gridLayout.setVerticalSpacing(20)
            gridLayout.setContentsMargins(0,0,0,0)
            # 设置网格大小
            for column in columns:
                gridLayout.setColumnMinimumWidth(
                    column, 224)
            for row in rows:
                gridLayout.setRowMinimumHeight(
                    row, 266)
            # 向网格中添加小部件
            for index, songerHeadPortrait in enumerate(songerHeadGroup_dict['songer_list']):
                x = index // 5
                y = index-5*x
                gridLayout.addWidget(
                    songerHeadPortrait, x, y, 1, 1)
            # 如果歌手数小于五，就在右侧增加弹簧
            offset = column - len(songerHeadGroup_dict['songer_list'])
            for i in range(offset):
                gridLayout.setColumnStretch(i+offset-1, 1)

            self.v_layout.addWidget(songerHeadGroup_dict['group'])
            self.v_layout.addSpacing(10)

        # 设置歌手头像视图窗口的布局
        self.songerHeadViewer.setLayout(self.v_layout)

        # 将歌手头像窗口添加到滚动区域中
        self.scrollArea.setWidget(self.songerHeadViewer)

        # 设置全局布局
        self.all_h_layout.addWidget(self.scrollArea)
        #self.all_h_layout.addWidget(self.scrollBar)
        self.setLayout(self.all_h_layout)

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\css\songerHeadPortraitViewer.qss', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)


class Widget(QWidget):
    """ 自定义滚动区域 """

    def __init__(self, parent=None):
        super().__init__(parent)

    """ def wheelEvent(self, e):
        print(self.parent().parent().parent().songerHeadGroup_dict_list[7]['group'].geometry()) """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongerHeadPortraitViewer()
    demo.show()
    sys.exit(app.exec_())
