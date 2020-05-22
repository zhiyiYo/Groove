import json
import os
import re
import sys

import pinyin
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBitmap, QImage, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QScrollArea,
    QScrollBar, QVBoxLayout, QWidget)

import get_album_cover
from album_card import AlbumCard
from get_album_info import AlbumInfo


class AlbumCardViewer(QWidget):
    """ 定义一个专辑卡视图 """

    def __init__(self, target_path, parent=None):
        super().__init__(parent)

        # 先扫描本地音乐的专辑封面
        self.getAlbumCover = get_album_cover.AlbumCover(target_path)
        # 获取专辑信息
        self.albumInfo = AlbumInfo()

        # 实例化布局
        self.gridLayout = QGridLayout()
        self.all_h_layout = QHBoxLayout()

        # 实例化滚动区域和滚动区域的窗口
        self.scrollArea = QScrollArea(self)
        self.albumView = QWidget()

        # 初始化小部件
        self.initWidget()
        # 创建专辑卡并将其添加到布局中
        self.checkIsFirstTimeToRun()
        self.createAlbumCards()
        self.initLayout()

        # 设置样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(1267, 638)
        self.scrollArea.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.scrollArea.verticalScrollBar().setSingleStep(30)

    def createAlbumCards(self):
        """ 将专辑卡添加到窗口中 """
        self.albumCardDict_list = []
        for albumInfo_dict in self.albumInfo.albumInfo_list:
            # 实例化专辑卡
            albumCard = AlbumCard(albumInfo_dict, self)
            album = albumInfo_dict['album']
            # 将含有专辑卡及其信息的字典插入列表
            self.albumCardDict_list.append({'albumCard': albumCard,
                                            'year': albumInfo_dict['year'],
                                            'songer': albumInfo_dict['songer'],
                                            'firstLetter': pinyin.get_initial(album)[0].upper()})

    def initLayout(self, column_num=5):
        """ 初始化布局 """
        columns = range(column_num)
        rows = range(
            (len(self.albumCardDict_list) - 1) // 5 + 1)
        self.gridLayout.setVerticalSpacing(11)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        # 设置网格大小
        for column in columns:
            self.gridLayout.setColumnMinimumWidth(
                column, 222)
        for row in rows:
            self.gridLayout.setRowMinimumHeight(
                row, 292)

        for index, albumCardDict in enumerate(self.albumCardDict_list):
            x = index // column_num
            y = index-column_num*x
            self.gridLayout.addWidget(
                albumCardDict['albumCard'], x, y, 1, 1)

        # 如果歌手数小于设定的列数，就在右侧增加弹簧
        offset = column_num - len(self.albumCardDict_list)
        for i in range(offset):
            self.gridLayout.setColumnStretch(i + offset - 1, 1)

        self.albumView.setLayout(self.gridLayout)
        self.scrollArea.setWidget(self.albumView)
        # 设置全局布局
        self.all_h_layout.addWidget(self.scrollArea)
        self.setLayout(self.all_h_layout)

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumCardViewer.qss', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def checkIsFirstTimeToRun(self):
        """ 检查是否初次运行程序，是的话就更改png文件 """
        with open('Data\\initProfile.json', encoding='utf-8') as f:
            self.profile = json.load(f)
        if self.profile['isFirstTimeToRun']:
            img = QImage()
            path = "resource\\Album Cover"
            for root, dirs, files in os.walk(path):
                for name in files:
                    if name.endswith(".png"):
                        print(path+'\\' + name)
                        img.load(path +'\\'+name)
                        img.save(path + '\\'+name)
            self.profile['isFirstTimeToRun'] = False
            # 更新配置文件
            with open('Data\initProfile.json', 'w', encoding='utf-8') as f:
                json.dump(self.profile, f)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = AlbumCardViewer('D:\\KuGou')
    demo.show()
    sys.exit(app.exec_())
