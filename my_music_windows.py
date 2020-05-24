import sys
import time
from PyQt5.QtCore import QPoint, QSize, Qt, QEvent
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,
                             QTabWidget, QVBoxLayout, QWidget)

from song_tab_interface import SongTabInterface
from songer_tab_interface import SongerTabInterface
from album_tab_interface import AlbumTabInterface


class MyMusicWindows(QTabWidget):
    """ 创建一个包含歌曲,歌手和专辑标签窗口的类 """

    def __init__(self, songs_folder, parent=None):
        super().__init__(parent)

        # 创建三个标签窗口
        self.songTag = SongTabInterface(songs_folder, self)
        self.songerTag = SongerTabInterface()
        self.albumTag = AlbumTabInterface(songs_folder)

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
        self.resize(1276, 733)
        # self.setMovable(True)
        self.setUsesScrollButtons(False)

        # 分配ID
        self.setObjectName('MyMusicWindows')

        # 设置监听
        # self.tabBar().installEventFilter(self)

    def setQss(self):
        """ 设置层叠样式表 """
        with open('resource\\css\\myMusicWindows.qss', 'r', encoding='utf-8') as f:
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
                self.setCurrentIndex(tabIndex)

        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    t1 = time.time()
    demo = MyMusicWindows('D:\\KuGou')
    demo.show()
    t2 = time.time()
    print(f'启动耗时{t2-t1:.3f}s')
    sys.exit(app.exec_())
