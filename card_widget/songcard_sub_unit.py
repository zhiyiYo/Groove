# coding:utf-8

""" songcard窗口的组件库 """

import sys
from time import sleep

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent,QEnterEvent
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QHBoxLayout,
                             QLabel, QPushButton, QToolButton, QWidget)
sys.path.append('..')
from Groove.my_widget.my_button import SongCardPlayButton,SongCardAddToButton

class SongNameCard(QWidget):
    """ 定义一个放置歌名和按钮的窗口 """

    def __init__(self, songName,parent=None):
        super().__init__(parent)

        # 设置右键菜单选择标志位
        self.contextMenuSelecting = False
        # 实例化小部件
        self.songNameCheckBox = QCheckBox(songName, self)
        self.buttonGroup = ButtonGroup(self)
        # 引用按钮
        self.playButton = self.buttonGroup.playButton
        self.addToButton = self.buttonGroup.addToButton
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
        self.setFixedWidth(342)
        self.widgetList=[self.songNameCheckBox,self.addToButton,self.playButton]
        # 设置按钮的绝对坐标
        self.buttonGroup.move(195,0)
        # 分配ID
        self.songNameCheckBox.setObjectName('songNameCheckBox')
        self.setObjectName('songNameCard')
        # 设置初始属性
        self.setWidgetState('leave and unClicked')

    def setWidgetState(self,buttonGroupState,checkBoxState='leave and unClicked',buttonState='unClicked'):
        """ 设置widget的state属性的状态,按钮的state属性只有点击clicked和未被点击unClicked两种状态,
            按钮窗口的state有四种状态:leave and unClicked、leave and clicked、enter and unClicked、enter and clicked
            复选框的state属性有clicked、enter and unClicked、leave and unClicked三种状态"""
        self.buttonGroup.setProperty('state',buttonGroupState)
        self.playButton.setProperty('state', buttonState)
        self.addToButton.setProperty('state', buttonState)
        self.songNameCheckBox.setProperty('state', checkBoxState)

    def setAllButtonHidden(self,hide:bool=True):
        """ 隐藏所有按钮 """
        if hide:
            self.playButton.hide()
            self.addToButton.hide()
        else:
            self.playButton.show()
            self.addToButton.show()


class YearTconDurationCard(QWidget):
    """ 定义一个包含年份、流派、时长的类 """

    def __init__(self,year,tcon, duration,parent=None):
        super().__init__(parent)

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

    def updateLabelText(self, songInfo_dict: dict):
        """ 更新标签的信息 """
        self.yearLabel.setText(songInfo_dict['year'])
        self.tconLabel.setText(songInfo_dict['tcon'])
        self.durationLabel.setText(songInfo_dict['duration'])
            
    def setWidgetState(self, labelState='unClicked'):
        """ 设置标签state属性的状态，流派、年份和时长三个标签的state属性只有点击和未点击两种状态 """
        for widget in self.widgetList:
            widget.setProperty('state', labelState)


class ButtonGroup(QWidget):
    """ 包含添加到和播放按钮的窗口 """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.playButton = SongCardPlayButton(self)
        self.addToButton = SongCardAddToButton(self)
        self.initWidget()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(147, 61)
        # 设置按钮的绝对坐标
        self.addToButton.move(86, 0)
        self.playButton.move(25, 0)
        # 分配ID
        self.setObjectName('buttonGroup')
        # 按钮窗口的state有四种状态:
        # leave and unClicked、leave and clicked、enter and unClicked、enter and clicked
        self.setProperty('state', 'leave and unClicked')
        # 隐藏按钮
        self.playButton.setHidden(True)
        self.addToButton.setHidden(True)

    def setQss(self):
        """ 设置样式 """
        with open('resource\\css\\songCard.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = SongNameCard('何十年後に「君」と出会っていなかったアナタに向けた歌')
    demo.show()
    sys.exit(app.exec_())
