# coding:utf-8

import sys
import time
from PyQt5.QtCore import QPoint, QSize, Qt, QEvent
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,
                             QTabWidget, QVBoxLayout, QWidget)

sys.path.append('..')
from Groove.tab_interface import AlbumTabInterface, SongTabInterface, SongerTabInterface


class MyMusicTabWidget(QTabWidget):
    """ 创建一个包含歌曲,歌手和专辑标签窗口的类 """

    def __init__(self, songs_folder, parent=None):
        super().__init__(parent)
        self.songs_folder = songs_folder

        # 创建三个标签窗口
        self.songTag = SongTabInterface(self.songs_folder)
        self.songerTag = SongerTabInterface()
        self.albumTag = AlbumTabInterface(self.songs_folder)

        # 初始化MyMusicWindows的属性
        self.initAttribute()
        # 将标签界面添加到子类中
        self.addTab(self.songTag, '歌曲')
        self.addTab(self.songerTag, '歌手')
        self.addTab(self.albumTag, '专辑')
        # 设置层叠样式表
        self.setQss()

    def initAttribute(self):
        """ 初始化子类的一些属性 """
        # 允许拖动标签
        self.resize(1276, 995-23)
        self.setUsesScrollButtons(False)

        # 分配ID
        self.setObjectName('MyMusicTabWidget')

        # 设置监听
        #self.tabBar().installEventFilter(self)

    def initTagLayout(self):
        """ 初始化页面布局 """
        self.songTagLayout = QHBoxLayout()
        self.songTagLayout.setContentsMargins(0, 0, 0, 0)
        self.songTag.setLayout(self.songTagLayout)
        self.currentLayout = self.songTagLayout

        self.songerTagLayout = QHBoxLayout()
        self.songerTagLayout.setContentsMargins(0, 0, 0, 0)
        self.songerTag.setLayout(self.songerTagLayout)

        self.albumTagLayout = QHBoxLayout()
        self.albumTagLayout.setContentsMargins(0, 0, 0, 0)
        self.albumTag.setLayout(self.albumTagLayout)

    def setQss(self):
        """ 设置层叠样式表 """
        with open('resource\\css\\myMusicTabWidget.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def eventFilter(self, obj, event):
        """ 鼠标松开时才切换界面 """
        event_cond = event.type() in [
            QEvent.MouseButtonPress, QEvent.MouseButtonRelease] and event.button() == Qt.LeftButton
        if obj == self.tabBar() and event_cond:
            tabIndex = self.tabBar().tabAt(event.pos())
            if event.type() == QEvent.MouseButtonPress and tabIndex != -1:
                return True
            elif event.type() == QEvent.MouseButtonRelease and tabIndex != -1:
                event = QMouseEvent(QEvent.MouseButtonPress,
                                event.pos(), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
                return False
        return super().eventFilter(obj,event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    t1 = time.time()
    demo = MyMusicTabWidget('D:\\KuGou')
    demo.show()
    t2 = time.time()
    print(f'启动耗时{t2-t1:.3f}s')
    sys.exit(app.exec_())
