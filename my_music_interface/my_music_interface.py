# coding:utf-8

import sys

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QIcon, QFont, QResizeEvent
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,
                             QScrollBar, QVBoxLayout, QWidget)

from tab_interface.my_music_tab_widget import MyMusicTabWidget
from my_widget.my_scroll_bar import ScrollBar


class MyMusicInterface(QWidget):
    """ 创建一个本地音乐分组界面 """
    def __init__(self, target_path_list: list, parent=None):
        super().__init__(parent)

        # 实例化一个包含三个标签界面的QTabWidget
        self.myMusicTabWidget = MyMusicTabWidget(target_path_list, self)
        # 引用三个视图的滚动条
        self.songCardList_vScrollBar = self.myMusicTabWidget.songTab.songCardListWidget.verticalScrollBar(
        )
        self.songerViewer_vScrollBar = self.myMusicTabWidget.songerTab.songerHeadPortraitViewer.scrollArea.verticalScrollBar(
        )
        self.albumViewer_vScrollBar = self.myMusicTabWidget.albumTab.albumCardViewer.scrollArea.verticalScrollBar(
        )
        # 实例化一个标签和三个竖直滚动条
        self.myMusicLabel = QLabel(self)
        self.song_scrollBar = ScrollBar(self.songCardList_vScrollBar, self)
        self.songer_scrollBar = ScrollBar(self.songerViewer_vScrollBar, self)
        self.album_scrollBar = ScrollBar(self.albumViewer_vScrollBar, self)
        self.scrollBar_list = [
            self.song_scrollBar, self.songer_scrollBar, self.album_scrollBar
        ]
        # 初始化
        self.initLayout()
        self.initWidget()
        self.setQss()

    def initLayout(self):
        """ 初始化布局 """
        self.myMusicLabel.move(30, 54)
        self.myMusicTabWidget.move(19, 136)
        for scrollBar in self.scrollBar_list:
            scrollBar.move(self.width() - scrollBar.width(), 40)

    def initWidget(self):
        """ 初始化小部件的属性 """
        self.resize(1300, 995 - 23 - 40)
        self.setMinimumHeight(630)
        self.setAttribute(Qt.WA_StyledBackground)
        if not self.parent():
            # 居中显示
            desktop = QApplication.desktop()
            self.move(int(desktop.width() / 2 - self.width() / 2),
                      int(desktop.height() / 2 - self.height() / 2) - 20)

        # 设置标签上的字
        self.myMusicLabel.setText('我的音乐')
        # 隐藏列表视图的滚动条
        self.myMusicTabWidget.songTab.songCardListWidget.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)

        # 设置滚动条高度
        self.adjustScrollBarHeight()

        # 先隐藏歌手视图的滚动条
        self.songer_scrollBar.hide()
        self.album_scrollBar.hide()

        # 标签窗口改变时也改变显示的滚动条
        self.myMusicTabWidget.stackedWidget.currentChanged.connect(
            self.changeTabEvent)

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
        with open('resource\\css\\myMusicInterface.qss', 'r',
                  encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def resizeEvent(self, e: QResizeEvent):
        """ 当窗口大小发生改变时隐藏小部件 """
        self.myMusicTabWidget.songTab.songCardListWidget.setLineWidth(
            self.width() - 33)
        self.adjustScrollBarHeight()
        self.myMusicTabWidget.resize(self.width() - 37, self.height() - 136)
        for scrollBar in self.scrollBar_list:
            scrollBar.move(self.width() - scrollBar.width(), 40)

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
    demo = MyMusicInterface(['D:\\KuGou\\test_audio'])
    demo.show()
    sys.exit(app.exec_())
