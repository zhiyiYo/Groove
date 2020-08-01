import sys
from json import load

from PyQt5.QtCore import Qt,QSize,pyqtSignal
from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem, QMenu, QAbstractItemView
from .song_card import SongCard

sys.path.append('..')
from Groove.my_widget.my_listWidget import ListWidget


class SongCardListWidget(ListWidget):
    """ 正在播放列表 """
    currentIndexChanged = pyqtSignal(int)

    def __init__(self, playlist:list, parent=None):
        super().__init__(parent)
        self.playlist = playlist
        self.currentIndex = 0
        self.songCard_list = []
        self.item_list = []
        # 创建歌曲卡
        self.createSongCards()
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
        # 将信号连接到槽函数
        # self.__connectSignalToSlot()

    def createSongCards(self):
        """ 创建歌曲卡 """
        for i in range(len(self.playlist)):
            # 添加空项目
            songInfo_dict = self.playlist[i]
            # 创建item和歌曲卡
            item = QListWidgetItem()
            songCard = SongCard(songInfo_dict)
            # 记录下标
            songCard.itemIndex = i  
            songCard.resize(1150, 60)
            item.setSizeHint(QSize(songCard.width(), 60))
            self.addItem(item)
            # 将项目的内容重置为自定义类
            self.setItemWidget(item, songCard)
            # 通过whatsthis记录每个项目对应的路径和下标
            item.setWhatsThis(str(songInfo_dict))
            # 将item和songCard添加到列表中
            self.songCard_list.append(songCard)
            self.item_list.append(item)
            # 信号连接到槽
            songCard.clicked.connect(self.__emitCurrentChangedSignal)
        if self.playlist:
            self.songCard_list[0].setPlay(True)

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\playInterfaceSongCardListWidget.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 更新item的尺寸 """
        for item in self.item_list:
            item.setSizeHint(QSize(self.width()-117, 60))
        super().resizeEvent(e)

    def __connectSignalToSlot(self):
        """ 将信号连接到槽函数 """
        # 点击歌曲卡发送信号并更新样式


    def __emitCurrentChangedSignal(self, index):
        """ 发送当前播放的歌曲卡下标变化信号，同时更新样式和歌曲信息卡 """
        # 发送下标更新信号
        self.currentIndexChanged.emit(index)
        self.setCurrentIndex(index)

    def setCurrentIndex(self, index):
        """ 设置当前播放歌曲下标，同时更新样式 """
        # 将之前播放的歌曲卡的播放状态设置为False
        self.songCard_list[self.currentIndex].setPlay(False)
        # 更新当前播放歌曲下标
        self.currentIndex = index
        # 更新当前播放歌曲卡样式
        self.songCard_list[index].setPlay(True)

    def setPlaylist(self, playlist: list):
        """ 更新播放列表 """
        self.playlist = playlist
        self.clear()
        self.item_list.clear()
        # 释放内存
        for songCard in self.songCard_list:
            songCard.deleteLater()
        self.songCard_list.clear()
        self.currentIndex = 0
        self.createSongCards()

    def updateSongCards(self, songInfoDict_list):
        """ 更新所有歌曲卡信息 """
        # 长度相等就更新信息，不相等就直接创建新的item
        print(
            f'新播放列表长度：{len(songInfoDict_list)},旧播放列表长度：{len(self.playlist)}')
        if len(songInfoDict_list) != len(self.playlist):
            self.setPlaylist(songInfoDict_list)
            print('创建新Item')
            return
        self.playlist = songInfoDict_list
        # 更新歌曲卡
        for i in range(len(self.playlist)):
            songInfo_dict = self.playlist[i]
            self.songCard_list[i].updateSongCard(songInfo_dict)
        self.currentIndex = 0
        self.songCard_list[0].setPlay(True)
        print('直接更新，不创建item')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
        songInfo_list = load(f)
    demo = SongCardListWidget(songInfo_list)
    demo.show()
    sys.exit(app.exec_())
