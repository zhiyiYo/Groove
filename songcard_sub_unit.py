# coding:utf-8

""" songcard窗口的组件库 """

import sys
from time import sleep

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QHBoxLayout,
                             QLabel, QMenu, QToolButton, QWidget)


class SongNameCard(QWidget):
    """ 定义一个放置歌名和按钮的窗口 """

    def __init__(self, songName):
        super().__init__()

        # 设置右键菜单选择标志位
        self.contextMenuSelecting = False
        # 设置单击标志位
        self.clicked = False

        # 实例化小部件
        self.setFixedWidth(342)
        self.songName = QCheckBox(songName, self)
        self.maskButton = QToolButton(self)
        self.playButton = QToolButton(self)
        self.addToButton = QToolButton(self)

        # 实例化布局
        self.all_h_layout = QHBoxLayout()

        # 初始化布局
        self.initLayout()

        # 初始化小部件
        self.initWidget()

    def initLayout(self):
        """ 初始化布局 """

        self.all_h_layout.addWidget(self.songName, Qt.AlignLeft)
        self.setLayout(self.all_h_layout)

    def initWidget(self):
        """ 初始化小部件 """
        # 设置按钮大小和图标
        self.addToButton.setIcon(QIcon('resource\\images\\black_addTo_bt.png'))
        self.playButton.setIcon(QIcon('resource\\images\\black_play_bt.png'))
        self.addToButton.setIconSize(QSize(61, 61))
        self.playButton.setIconSize(QSize(61, 61))
        self.addToButton.setFixedSize(61, 61)
        self.playButton.setFixedSize(61, 61)
        self.maskButton.setFixedSize(25, 61)

        # 设置按钮的绝对坐标
        self.addToButton.move(281, 0)
        self.playButton.move(220, 0)
        self.maskButton.move(195, 0)

        # 隐藏按钮
        self.playButton.setHidden(True)
        self.addToButton.setHidden(True)
        self.maskButton.setHidden(True)

        # 分配ID
        self.setObjectName('songNameCard')
        self.songName.setObjectName('songNameCheckbox')
        self.addToButton.setObjectName('addToButton')
        self.playButton.setObjectName('playButton')
        self.maskButton.setObjectName('maskButton')

    def showIndicator(self):
        """ 当鼠标光标移动到歌曲卡上时显示复选框 """

        with open('resource\\css\\selectedSongCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
        self.songName.setStyleSheet(qss)

    def hideIndicator(self):
        """ 当鼠标离开歌曲卡上时隐藏复选框 """
        with open('resource\\css\\hideIndicator.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
        self.songName.setStyleSheet(qss)


class TconYearDurationCard(QWidget):
    """ 定义一个包含年份、流派、时长的类 """

    def __init__(self, tcon, year, duration):
        super().__init__()

        self.setFixedWidth(400)
        # 实例化三个标签
        self.tconLabel = QLabel(tcon, self)
        self.yearLabel = QLabel(year, self)
        self.durationLabel = QLabel(duration, self)

        # 实例化布局
        self.h_layout = QHBoxLayout(self)

        # 初始化布局
        self.initLayout()

    def initLayout(self):
        """ 初始化布局 """
        self.h_layout.addWidget(self.yearLabel, 0, Qt.AlignLeft)
        self.h_layout.addSpacing(5)
        self.h_layout.addWidget(self.tconLabel, 0, Qt.AlignLeft)
        self.h_layout.addStretch(1)
        self.h_layout.addWidget(self.durationLabel, 0, Qt.AlignRight)

        self.setLayout(self.h_layout)

    def initWidget(self):
        """ 初始化小部件 """

        # 分配ID
        self.tconLabel.setObjectName('tconLabel')
        self.yearLabel.setObjectName('yearLabel')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = SongNameCard('何十年後に「君」と出会っていなかったアナタに向けた歌')
    demo.show()
    sys.exit(app.exec_())
