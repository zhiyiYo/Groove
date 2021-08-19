# coding:utf-8
from typing import List

from app.components.dialog_box.song_property_dialog import SongPropertyDialog
from app.components.list_widget import ListWidget
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QApplication, QListWidgetItem

from .menu import Menu
from .song_card import SongCard


class SongListWidget(ListWidget):
    """ 正在播放列表 """

    emptyChanged = pyqtSignal(bool)                     # 歌曲列表 空/非空 变化
    removeSongSig = pyqtSignal(int)                     # 移除歌曲
    currentIndexChanged = pyqtSignal(int)               # 当前播放的变化
    isAllCheckedChanged = pyqtSignal(bool)              # 歌曲卡卡全部选中改变
    selectionModeStateChanged = pyqtSignal(bool)        # 进入或退出选择模式
    checkedSongCardNumChanged = pyqtSignal(int)         # 选中的歌曲卡数量改变
    switchToAlbumInterfaceSig = pyqtSignal(str, str)    # albumName, singerName
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)   # 将歌曲添加到新的自定义播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 将歌曲添加到已存在的自定义播放列表

    def __init__(self, songInfo_list: list, parent=None):
        super().__init__(parent)
        self.songInfo_list = songInfo_list
        self.currentIndex = 0
        self.item_list = []
        self.songCard_list = []  # type:List[SongCard]
        self.checkedSongCard_list = []  # type:List[SongCard]
        self.isInSelectionMode = False
        self.isAllSongCardsChecked = False
        # 创建歌曲卡
        self.createSongCards()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1150 + 60, 800)
        # 设置内边距
        self.setViewportMargins(30, 0, 30, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__setQss()

    def createSongCards(self):
        """ 创建歌曲卡 """
        for songInfo in self.songInfo_list:
            self.appendOneSongCard(songInfo)
        if self.songInfo_list:
            self.songCard_list[self.currentIndex].setPlay(True)
        self.resize(1200, 800)

    def __setQss(self):
        """ 设置层叠样式 """
        with open("app/resource/css/playing_interface_song_list_widget.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 更新item的尺寸 """
        for item in self.item_list:
            item.setSizeHint(QSize(self.width() - 60, 60))
        super().resizeEvent(e)

    def __emitCurrentChangedSignal(self, index):
        """ 发送当前播放的歌曲卡下标变化信号，同时更新样式和歌曲信息卡 """
        # 发送下标更新信号
        self.currentIndexChanged.emit(index)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 显示右击菜单 """
        hitIndex = self.indexAt(e.pos()).column()
        if hitIndex > -1:
            menu = Menu(self)
            self.__connectContextMenuSignalToSlot(menu)
            if self.currentRow() == len(self.songInfo_list) - 1:
                menu.moveDownAct.setEnabled(False)
            if self.currentRow() == 0:
                menu.moveUpAct.setEnabled(False)
            menu.exec_(e.globalPos())

    def showSongPropertyDialog(self, songCard: SongCard = None):
        """ 显示属性面板 """
        songInfo = self.songCard_list[self.currentRow(
        )].songInfo if not songCard else songCard.songInfo
        w = SongPropertyDialog(songInfo, self.window())
        w.exec_()

    def removeSongCard(self, index):
        """ 移除选一个歌曲卡 """
        # 更新下标
        for songCard in self.songCard_list[index+1:]:
            songCard.itemIndex -= 1

        # 更新歌曲卡选中状态
        if self.currentIndex > index:
            self.currentIndex -= 1
        elif self.currentIndex == index:
            self.setCurrentIndex(index-1)

        # 删除歌曲卡
        self.songInfo_list.pop(index)
        songCard = self.songCard_list.pop(index)
        songCard.deleteLater()
        self.item_list.pop(index)
        self.takeItem(index)

        # 发送信号
        self.removeSongSig.emit(index)

    def setCurrentIndex(self, index: int):
        """ 设置当前播放歌曲下标，同时更新样式 """
        if not self.songCard_list or index == self.currentIndex:
            return
        # 将之前播放的歌曲卡的播放状态设置为False
        self.songCard_list[self.currentIndex].setPlay(False)
        # 更新当前播放歌曲下标
        self.currentIndex = index
        # 更新当前播放歌曲卡样式
        self.songCard_list[index].setPlay(True)

    def setPlaylist(self, playlist: list, isResetIndex: bool = True):
        """ 直接清空并更新播放列表 """
        self.songInfo_list = playlist
        self.clearSongCards(isResetIndex)
        self.createSongCards()

    def clearSongCards(self, isResetIndex: bool = True):
        """ 清空歌曲卡 """
        self.item_list.clear()
        self.clear()
        # 释放内存
        for songCard in self.songCard_list:
            songCard.deleteLater()
        self.songCard_list.clear()
        self.currentIndex = 0 if isResetIndex else self.currentIndex

    def updateSongCards(self, songInfo_list: list, isResetIndex=True, index=0):
        """ 更新所有歌曲卡信息 """
        # 长度相等就更新信息，不相等就根据情况创建或者删除item
        if self.songCard_list:
            self.songCard_list[self.currentIndex].setPlay(False)

        oldSongNum = len(self.songInfo_list)
        newSongNum = len(songInfo_list)

        # 添加item
        if newSongNum > oldSongNum:
            for songInfo in songInfo_list[oldSongNum:]:
                self.appendOneSongCard(songInfo)
                QApplication.processEvents()
        # 删除多余的item
        elif newSongNum < oldSongNum:
            for i in range(oldSongNum - 1, newSongNum - 1, -1):
                self.item_list.pop()
                songCard = self.songCard_list.pop()
                songCard.deleteLater()
                self.takeItem(i)

        # 更新部分歌曲卡
        self.songInfo_list = songInfo_list
        n = oldSongNum if newSongNum > oldSongNum else newSongNum
        for i in range(n):
            songInfo_dict = self.songInfo_list[i]
            self.songCard_list[i].updateSongCard(songInfo_dict)

        # 更新样式和当前下标
        self.currentIndex = index if isResetIndex else self.currentIndex
        if self.songInfo_list:
            self.songCard_list[self.currentIndex].setPlay(True)

    def __switchToAlbumInterface(self, albumName: str, singerName: str):
        """ 切换到专辑界面 """
        self.switchToAlbumInterfaceSig.emit(albumName, singerName)

    def updateOneSongCard(self, newSongInfo: dict):
        """ 更新一个歌曲卡 """
        for i, songInfo in enumerate(self.songInfo_list):
            if songInfo["songPath"] == newSongInfo["songPath"]:
                self.songInfo_list[i] = newSongInfo
                self.songCard_list[i].updateSongCard(newSongInfo)

    def updateMultiSongCards(self, newSongInfo_list: list):
        """ 更新多个的歌曲卡 """
        for newSongInfo in newSongInfo_list:
            self.updateOneSongCard(newSongInfo)

    def appendOneSongCard(self, songInfo: dict):
        """ 在歌曲列表视图尾部添加一个歌曲卡 """
        songCard = SongCard(songInfo)
        songCard.itemIndex = len(self.songCard_list)
        songCard.resize(1150, 60)

        item = QListWidgetItem()
        item.setSizeHint(QSize(songCard.width(), 60))
        self.addItem(item)
        self.setItemWidget(item, songCard)

        self.songCard_list.append(songCard)
        self.item_list.append(item)

        # 信号连接到槽
        songCard.aniStartSig.connect(
            lambda: self.songCard_list[self.currentIndex].setPlay(False))
        songCard.clicked.connect(self.__emitCurrentChangedSignal)
        songCard.switchToAlbumInterfaceSig.connect(
            self.__switchToAlbumInterface)
        songCard.addSongToCustomPlaylistSig.connect(
            lambda name, songInfo: self.addSongsToCustomPlaylistSig.emit(name, [songInfo]))
        songCard.addSongToNewCustomPlaylistSig.connect(
            lambda songInfo: self.addSongsToNewCustomPlaylistSig.emit([songInfo]))
        songCard.checkedStateChanged.connect(self.onCheckedStateChanged)

    def onCheckedStateChanged(self, index: int, isChecked: bool):
        """ 歌曲卡选中状态改变对应槽函数 """
        songCard = self.songCard_list[index]

        # 如果歌曲卡不在选中的歌曲列表中且该歌曲卡变为选中状态就将其添加到列表中
        if songCard not in self.checkedSongCard_list and isChecked:
            self.checkedSongCard_list.append(songCard)
            self.checkedSongCardNumChanged.emit(len(self.checkedSongCard_list))
        # 如果歌曲卡已经在列表中且该歌曲卡变为非选中状态就弹出该歌曲卡
        elif songCard in self.checkedSongCard_list and not isChecked:
            self.checkedSongCard_list.remove(songCard)
            self.checkedSongCardNumChanged.emit(len(self.checkedSongCard_list))

        isAllChecked = (len(self.checkedSongCard_list)
                        == len(self.songCard_list))
        if isAllChecked != self.isAllSongCardsChecked:
            self.isAllSongCardsChecked = isAllChecked
            self.isAllCheckedChanged.emit(isAllChecked)

        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            # 所有歌曲卡进入选择模式
            self.__setAllSongCardSelectionModeOpen(True)
            self.selectionModeStateChanged.emit(True)
            self.isInSelectionMode = True
        elif not self.checkedSongCard_list:
            # 所有歌曲卡退出选择模式
            self.__setAllSongCardSelectionModeOpen(False)
            # 发送信号要求隐藏状态状态栏
            self.selectionModeStateChanged.emit(False)
            self.isInSelectionMode = False

    def __setAllSongCardSelectionModeOpen(self, isOpenSelectionMode: bool):
        """ 设置所有歌曲卡是否进入选择模式 """
        # 更新光标样式
        cursor = Qt.ArrowCursor if isOpenSelectionMode else Qt.PointingHandCursor
        for songCard in self.songCard_list:
            songCard.setSelectionModeOpen(isOpenSelectionMode)
            songCard.albumLabel.setCursor(cursor)
            songCard.singerLabel.setCursor(cursor)

    def setAllSongCardCheckedState(self, isAllChecked: bool):
        """ 设置所有的歌曲卡checked状态 """
        if self.isAllSongCardsChecked == isAllChecked:
            return
        self.isAllSongCardsChecked = isAllChecked
        for songCard in self.songCard_list:
            songCard.setChecked(isAllChecked)

    def unCheckAllSongCards(self):
        """ 取消所有歌曲卡选中状态 """
        for songCard in self.songCard_list:
            songCard.setChecked(False)

    def __connectContextMenuSignalToSlot(self, menu: Menu):
        """ 将信号连接到槽函数 """
        # 右击菜单信号连接到槽函数
        menu.playAct.triggered.connect(
            lambda: self.__emitCurrentChangedSignal(self.currentRow()))
        menu.propertyAct.triggered.connect(self.showSongPropertyDialog)
        menu.removeAct.triggered.connect(
            lambda: self.removeSongCard(self.currentRow()))
        menu.showAlbumAct.triggered.connect(
            lambda: self.__switchToAlbumInterface(
                self.songCard_list[self.currentRow()].album,
                self.songCard_list[self.currentRow()].singer,
            )
        )
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(
                name, [self.songInfo_list[self.currentRow()]]))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(
                [self.songInfo_list[self.currentRow()]]))
