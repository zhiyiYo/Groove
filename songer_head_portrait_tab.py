import sys
import json
from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QBitmap, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QGridLayout, QWidget, QScrollArea, QHBoxLayout

from songer_card import SongerCard


class SongerHeadPortraitTab(QWidget):
    """ 创建一个包含所有歌手头像的界面 """

    def __init__(self):
        super().__init__()

        self.resize(1267, 684)
        self.setStyleSheet("background:white")
        # 实例化一个滚动区域
        self.scrollArea = QScrollArea(self)
        self.songerHeadViewer = QWidget()

        # 实例化布局
        self.all_layout = QHBoxLayout()
        self.gridLayout = QGridLayout()

        # 初始化歌手头像和布局
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        """ 初始化歌手头像 """
        # 从json文件中读取歌手信息
        with open('Data\\songerInfo.json', encoding='utf-8') as f:
            songerInfo_list = json.load(f)

        # 创建歌手头像列表
        self.songerHeadPortrait_list = []
        for songerInfo_dict in songerInfo_list:
            songerName = songerInfo_dict['songer']
            songerPicPath = 'resource\\Songer Photos\\' + \
                songerName+'\\'+songerInfo_dict['songer']+'.jpg'
            songerCard = SongerCard(songerPicPath, songerName)
            self.songerHeadPortrait_list.append(songerCard)

    def initLayout(self):
        """ 初始化布局 """

        for index, songerHeadPortrait in enumerate(self.songerHeadPortrait_list):
            x = index // 5
            y = index-5*x
            self.gridLayout.setRowMinimumHeight(x, 266)
            self.gridLayout.setColumnMinimumWidth(y, 224)
            # 向网格中添加小部件
            self.gridLayout.addWidget(songerHeadPortrait, x, y, 1, 1)

        self.songerHeadViewer.setLayout(self.gridLayout)
        self.scrollArea.setWidget(self.songerHeadViewer)
        self.all_layout.addWidget(self.scrollArea)
        self.setLayout(self.all_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongerHeadPortraitTab()
    demo.show()
    sys.exit(app.exec_())
