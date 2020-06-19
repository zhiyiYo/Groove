# coding:utf-8

""" songcard窗口的组件库 """

import sys
from time import sleep

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QHBoxLayout,
                             QLabel, QToolButton, QWidget)


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
        self.songNameCheckBox = QCheckBox(songName, self)
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

        self.all_h_layout.addWidget(self.songNameCheckBox, Qt.AlignLeft)
        self.setLayout(self.all_h_layout)

    def initWidget(self):
        """ 初始化小部件 """
        self.widgetList=[self.songNameCheckBox,self.addToButton,self.playButton,self.maskButton]

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
        self.songNameCheckBox.setObjectName('songNameCheckbox')
        self.addToButton.setObjectName('addToButton')
        self.playButton.setObjectName('playButton')
        self.maskButton.setObjectName('maskButton')
        self.setObjectName('songNameCard')

        # 设置初始属性
        self.setWidgetState()

    def setWidgetState(self,checkBoxState='leave and unClicked',buttonState='unClicked'):
        """ 设置widget的state属性的状态,按钮的state属性只有点击clicked和未被点击unClicked两种状态,
            复选框的state属性有clicked、enter and unClicked、leave and unClicked三种状态"""
        for widget in self.widgetList:
            if widget != self.songNameCheckBox:
                widget.setProperty('state', buttonState)
            else:
                widget.setProperty('state', checkBoxState)


class YearTconDurationCard(QWidget):
    """ 定义一个包含年份、流派、时长的类 """

    def __init__(self,year,tcon, duration):
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
        self.initWidget()

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
        self.widgetList=[self.tconLabel, self.yearLabel, self.durationLabel]
        # 分配ID
        self.tconLabel.setObjectName('tconLabel')
        self.yearLabel.setObjectName('yearLabel')
        # 设置初始属性
        self.setWidgetState()
            
    def setWidgetState(self, labelState='unClicked'):
        """ 设置标签state属性的状态，流派、年份和时长三个标签的state属性只有点击和未点击两种状态 """
        for widget in self.widgetList:
            widget.setProperty('state', labelState)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = SongNameCard('何十年後に「君」と出会っていなかったアナタに向けた歌')
    demo.show()
    sys.exit(app.exec_())
