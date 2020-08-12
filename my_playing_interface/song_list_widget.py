import sys
from json import load
from enum import Enum

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QListWidget,
                             QListWidgetItem, QMenu)

from my_widget.my_listWidget import ListWidget
from my_dialog_box import PropertyPanel

from .song_card import SongCard
from .menu import Menu


class SongListWidget(ListWidget):
    """ 正在播放列表 """
    currentIndexChanged = pyqtSignal(int)
    removeItemSignal = pyqtSignal(int)
    switchToAlbumInterfaceSig = pyqtSignal(str)

    def __init__(self, playlist: list, parent=None):
        super().__init__(parent)
        self.playlist = playlist
        self.currentIndex = 0
        self.songCard_list = []
        self.item_list = []
        self.updateMode = UpdateMode.CREATE_ALL_NEW_CARDS
        # 创建右击菜单
        self.menu = Menu(self)
        # 创建歌曲卡
        # self.createSongCards()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1150, 800)
        # self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.__setQss()
        # 将信号连接到槽函数
        self.__connectSignalToSlot()

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
            songCard.switchToAlbumInterfaceSig.connect(
                self.__switchToAlbumInterface)
        if self.playlist:
            self.songCard_list[0].setPlay(True)
        self.resize(1200, 800)
        # 更新歌曲卡更新方式
        self.updateMode = UpdateMode.UPDATE_ALL_CARDS

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\playInterfaceSongCardListWidget.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 更新item的尺寸 """
        for item in self.item_list:
            item.setSizeHint(QSize(self.width(), 60))
        super().resizeEvent(e)

    def __connectSignalToSlot(self):
        """ 将信号连接到槽函数 """
        # 右击菜单信号连接到槽函数
        self.menu.playAct.triggered.connect(
            lambda: self.__emitCurrentChangedSignal(self.currentRow()))
        self.menu.propertyAct.triggered.connect(self.__showPropertyPanel)
        self.menu.removeAct.triggered.connect(
            lambda: self.__removeSongCard(self.currentRow()))
        self.menu.showAlbumAct.triggered.connect(
            lambda: self.__switchToAlbumInterface(
                self.songCard_list[self.currentRow()].albumLabel.text()))

    def __emitCurrentChangedSignal(self, index):
        """ 发送当前播放的歌曲卡下标变化信号，同时更新样式和歌曲信息卡 """
        # 发送下标更新信号
        self.currentIndexChanged.emit(index)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 显示右击菜单 """
        hitIndex = self.indexAt(e.pos()).column()
        if hitIndex > -1:
            self.menu.moveUpAct.setEnabled(True)
            self.menu.moveDownAct.setEnabled(True)
            if self.currentRow() == len(self.playlist) - 1:
                self.menu.moveDownAct.setEnabled(False)
            if self.currentRow() == 0:
                self.menu.moveUpAct.setEnabled(False)
            self.menu.exec_(e.globalPos())

    def __showPropertyPanel(self):
        """ 显示属性面板 """
        songInfo = self.songCard_list[self.currentRow()].songInfo
        propertyPanel = PropertyPanel(songInfo, self.window())
        propertyPanel.exec_()

    def __removeSongCard(self, index):
        """ 移除选中的一个歌曲卡 """
        # 记录下当前播放列表长度
        playlistLen = len(self.playlist)
        self.playlist.pop(index)
        songCard = self.songCard_list.pop(index)
        songCard.deleteLater()
        self.item_list.pop(index)
        self.takeItem(index)
        # 更新下标
        for i in range(index, len(self.songCard_list)):
            self.songCard_list[i].itemIndex = i
        if self.currentIndex > index:
            self.currentIndex -= 1
        elif self.currentIndex == index:
            # 如果被移除的是最后一首歌就将更新的下标减一
            if index == playlistLen - 1:
                self.currentIndex -= 1
                self.setCurrentIndex(index-1)
            else:
                self.setCurrentIndex(index)
        # 发送信号
        self.removeItemSignal.emit(index)

    def setCurrentIndex(self, index):
        """ 设置当前播放歌曲下标，同时更新样式 """
        if self.songCard_list:
            # 将之前播放的歌曲卡的播放状态设置为False
            self.songCard_list[self.currentIndex].setPlay(False)
            # 更新当前播放歌曲下标
            self.currentIndex = index
            # 更新当前播放歌曲卡样式
            self.songCard_list[index].setPlay(True)

    def setPlaylist(self, playlist: list):
        """ 直接清空并更新播放列表 """
        self.playlist = playlist
        self.clearSongCards()
        self.createSongCards()

    def clearSongCards(self):
        """ 清空歌曲卡 """
        self.item_list.clear()
        self.clear()
        # 释放内存
        for songCard in self.songCard_list:
            songCard.deleteLater()
        self.songCard_list.clear()
        self.currentIndex = 0

    def updateSongCards(self, songInfoDict_list):
        """ 更新所有歌曲卡信息 """
        # 长度相等就更新信息，不相等就根据情况创建或者删除item
        if self.songCard_list:
            self.songCard_list[self.currentIndex].setPlay(False)
        deltaLen = len(songInfoDict_list) - len(self.playlist)
        if deltaLen > 0:
            # 添加item
            for i in range(len(self.playlist), len(self.playlist) + deltaLen):
                # 添加空项目
                songInfo_dict = songInfoDict_list[i]
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
                songCard.switchToAlbumInterfaceSig.connect(
                    self.__switchToAlbumInterface)
        elif deltaLen < 0:
            # 删除多余的item
            for i in range(len(self.playlist) - 1, len(self.playlist) + deltaLen - 1, -1):
                self.item_list.pop()
                songCard = self.songCard_list.pop()
                songCard.deleteLater()
                self.takeItem(i)
        # 更新部分歌曲卡
        self.playlist = songInfoDict_list
        iterRange = range(
            len(self.playlist) - deltaLen) if deltaLen > 0 else range(len(self.playlist))
        for i in iterRange:
            songInfo_dict = self.playlist[i]
            self.songCard_list[i].updateSongCard(songInfo_dict)
        # 更新样式和当前下标
        self.currentIndex = 0
        self.songCard_list[0].setPlay(True)

    def __switchToAlbumInterface(self, albumName: str):
        """ 切换到专辑界面 """
        self.switchToAlbumInterfaceSig.emit(albumName)


class UpdateMode(Enum):
    """ 更新歌曲卡方式枚举类 """
    CREATE_ALL_NEW_CARDS = 0
    UPDATE_ALL_CARDS = 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
        songInfo_list = load(f)
    demo = SongListWidget(songInfo_list)
    demo.show()
    sys.exit(app.exec_())
