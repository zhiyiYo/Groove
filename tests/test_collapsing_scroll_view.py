# coding:utf-8
import sys
import json

from components.scroll_area import ScrollArea
from View.playlist_interface.playlist_info_bar import PlaylistInfoBar
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication


class ListWidget(QListWidget):

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlternatingRowColors(True)
        self.setViewportMargins(30, 0, 30, 0)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.item_list = []

        for i in range(20):
            item = QListWidgetItem(f'item {i+1}', self)
            item.setSizeHint(QSize(1240, 60))
            self.item_list.append(item)

        self.setFixedHeight(len(self.item_list)*60+116)

    def wheelEvent(self, e):
        return


class Demo(ScrollArea):

    def __init__(self, playlist: dict, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget(self)
        self.vBox = QVBoxLayout(self.scrollWidget)
        self.listWidget = ListWidget(self.scrollWidget)
        self.infoBar = PlaylistInfoBar(playlist, self)
        self.playBar = QWidget(self)

        self.playBar.setFixedHeight(116)
        self.playBar.setStyleSheet('background:rgba(0,112,200,0.7)')

        self.vBox.addWidget(self.listWidget)
        self.vBox.setContentsMargins(0, 430, 0, 0)

        self.setWidget(self.scrollWidget)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalScrollBar().valueChanged.connect(self.onScrollValueChanged)
        self.resize(1300, 900)

    def onScrollValueChanged(self, value):
        h = 385-value
        if h > 82:
            self.infoBar.resize(self.width(), h)

    def resizeEvent(self, e):
        for item in self.listWidget.item_list:
            item.setSizeHint(QSize(self.width()-60, 60))
        self.listWidget.resize(self.width(), self.listWidget.height())
        self.scrollWidget.resize(self.width(), self.listWidget.height()+430)
        self.infoBar.resize(self.width(), self.infoBar.height())
        self.playBar.resize(self.width(), self.playBar.height())
        self.playBar.move(0, self.height()-self.playBar.height())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open("Playlists/我喜欢.json", encoding="utf-8") as f:
        playlist = json.load(f)
    w = Demo(playlist)
    w.show()
    sys.exit(app.exec_())
