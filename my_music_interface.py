# coding:utf-8

import sys
import time
from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QIcon, QFont, QResizeEvent
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,
                             QScrollBar, QVBoxLayout, QWidget)

from my_music_tab_widget import MyMusicTabWidget
from my_dialog_box.window_mask import WindowMask
from my_widget.my_scrollBar import ScrollBar


class MyMusicInterface(QWidget):
    """ 创建一个本地音乐分组界面 """

    def __init__(self, songs_folder, parent=None):
        super().__init__(parent)

        # 实例化一个包含三个标签界面的QTabWidget
        self.myMusicTabWidget = MyMusicTabWidget(songs_folder, self)
        # 引用三个视图的滚动条
        self.songCardList_vScrollBar = self.myMusicTabWidget.songTag.songCardListWidget.verticalScrollBar()
        self.songerViewer_vScrollBar = self.myMusicTabWidget.songerTag.songerHeadPortraitViewer.scrollArea.verticalScrollBar()
        self.albumViewer_vScrollBar = self.myMusicTabWidget.albumTag.albumCardViewer.scrollArea.verticalScrollBar()

        # 实例化一个标签和三个竖直滚动条
        self.myMusicLabel = QLabel(self)
        self.song_scrollBar = ScrollBar(self.songCardList_vScrollBar, self)
        self.songer_scrollBar = ScrollBar(self.songerViewer_vScrollBar, self)
        self.album_scrollBar = ScrollBar(self.albumViewer_vScrollBar, self)

        # 实例化三个布局
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        self.all_v_layout = QVBoxLayout()

        # 初始化
        self.initLayout()
        self.initWidget()

        # 设置样式
        self.setQss()

    def initLayout(self):
        """ 初始化布局 """
        self.v_layout.addWidget(self.myMusicLabel)
        self.v_layout.addSpacing(8)
        self.v_layout.addWidget(self.myMusicTabWidget)

        self.h_layout.addLayout(self.v_layout)
        self.h_layout.addSpacing(11)
        self.h_layout.addWidget(self.song_scrollBar, 0, Qt.AlignRight)
        self.h_layout.addWidget(self.songer_scrollBar, 0, Qt.AlignRight)
        self.h_layout.addWidget(self.album_scrollBar, 0, Qt.AlignRight)
        self.h_layout.setContentsMargins(20, 0, 1, 0)

        # 留下标题栏的占位空间
        self.all_v_layout.addSpacing(40)
        self.all_v_layout.addLayout(self.h_layout)
        self.all_v_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.all_v_layout)

    def initWidget(self):
        """ 初始化小部件的属性 """
        self.resize(1300, 995-23-40)
        self.setMinimumHeight(630)
        self.setAttribute(Qt.WA_StyledBackground)
        if not self.parent():
            # 居中显示
            desktop = QApplication.desktop()
            self.move(int(desktop.width() / 2 - self.width() / 2),
                    int(desktop.height() / 2 - self.height() / 2)-20)

        # 设置标签上的字
        self.myMusicLabel.setText('我的音乐')
        # 隐藏列表视图的滚动条
        self.myMusicTabWidget.songTag.songCardListWidget.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)

        # 设置滚动条高度
        self.adjustScrollBarHeight()

        # 先隐藏歌手视图的滚动条
        self.songer_scrollBar.hide()
        self.album_scrollBar.hide()

        # 标签窗口改变时也改变显示的滚动条
        self.myMusicTabWidget.currentChanged.connect(self.changeTabEvent)

        # 分配ID
        self.setObjectName('musicGroupInterface')
        self.myMusicLabel.setObjectName('myMusicLabel')
        self.song_scrollBar.setObjectName('songScrollBar')
        self.songer_scrollBar.setObjectName('songerScrollBar')
        self.album_scrollBar.setObjectName('albumScrollBar')

    def adjustScrollBarHeight(self):
        """ 调整滚动条高度 """
        self.song_scrollBar.adjustSrollBarHeight()
        self.songer_scrollBar.adjustSrollBarHeight()
        self.album_scrollBar.adjustSrollBarHeight()

    def setQss(self):
        """ 设置层叠样式表 """
        with open('resource\\css\\myMusicInterface.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def resizeEvent(self, e: QResizeEvent):
        """ 当窗口大小发生改变时隐藏小部件 """
        self.myMusicTabWidget.songTag.songCardListWidget.setLineWidth(
            self.width() - 33)
        self.adjustScrollBarHeight()

        """ if self.width() < 1156:
            # 窗口宽度大于956px且小于1156时显示年份标签，隐藏专辑按钮
            for song_card in self.myMusicTabWidget.songTag.songCardListWidget.songCard_list:
                #song_card.albumLabel.hide()
                song_card.yearTconDuration.durationLabel.hide()

        elif self.width() > 1156:
            # 窗口宽度大于1156时显示年份标签，显示专辑按钮
            for song_card in self.myMusicTabWidget.songTag.songCardListWidget.songCard_list:
                song_card.albumLabel.show()
                song_card.yearTconDuration.durationLabel.show() """

    def changeTabEvent(self, index):
        """ 当前标签窗口改变时更改滚动条的绑定对象 """
        if index == 0:
            self.song_scrollBar.show()
            self.songer_scrollBar.hide()
            self.album_scrollBar.hide()
        elif index == 1:
            self.song_scrollBar.hide()
            self.songer_scrollBar.show()
            self.album_scrollBar.hide()
        elif index == 2:
            self.song_scrollBar.hide()
            self.songer_scrollBar.hide()
            self.album_scrollBar.show()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    font = QFont(QApplication.font())
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    demo = MyMusicInterface('D:\\KuGou\\')
    demo.show()
    sys.exit(app.exec_())
