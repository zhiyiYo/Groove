import sys
from json import load

from PyQt5.QtCore import Qt,QSize
from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem, QMenu, QAbstractItemView
from song_card import SongCard

sys.path.append('..')
from Groove.my_widget.my_listWidget import ListWidget


class SongCardListWidget(ListWidget):
    """ 正在播放列表 """

    def __init__(self, playlist:list, parent=None):
        super().__init__(parent)
        self.playlist = playlist
        self.currentIndex = 0
        self.songCard_list = []
        self.item_list = []
        # 创建歌曲卡
        self.__createSongCards()
        # 初始化
        self.__initWidget()
        
    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1367,800)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.__setQss()

    def __createSongCards(self):
        """ 创建歌曲卡 """
        for i in range(len(self.playlist)):
            # 添加空项目
            songInfo_dict = self.playlist[i]
            self.item = QListWidgetItem()
            # 将项目的内容重置为自定义类
            self.songCard = SongCard(songInfo_dict)
            self.songCard.resize(1150, 60)
            self.item.setSizeHint(QSize(self.songCard.width(), 60))
            self.addItem(self.item)
            self.setItemWidget(self.item, self.songCard)
            # 通过whatsthis记录每个项目对应的路径和下标
            self.item.setWhatsThis(str(songInfo_dict))
            # 将项目添加到项目列表中
            self.songCard_list.append(self.songCard)
            self.item_list.append(self.item)

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\playInterfaceSongCardListWidget.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 更新item的尺寸 """
        for item in self.item_list:
            item.setSizeHint(QSize(self.width()-117, 60))
        super().resizeEvent(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
        songInfo_list = load(f)
    demo = SongCardListWidget(songInfo_list)
    demo.show()
    sys.exit(app.exec_())
