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

    currentIndexChanged = pyqtSignal(int)
    removeItemSignal = pyqtSignal(int)
    selectionModeStateChanged = pyqtSignal(bool)      # 进入或退出选择模式
    checkedSongCardNumChanged = pyqtSignal(int)     # 选中的歌曲卡数量改变
    switchToAlbumInterfaceSig = pyqtSignal(str, str) # albumName, songerName
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)  # 将歌曲添加到新的自定义播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 将歌曲添加到已存在的自定义播放列表

    def __init__(self, playlist: list, parent=None):
        super().__init__(parent)
        self.playlist = playlist
        self.currentIndex = 0
        self.item_list = []
        self.songCard_list = []  # type:List[SongCard]
        self.checkedSongCard_list = []  # type:List[SongCard]
        self.isInSelectionMode = False
        self.isAllSongCardsChecked = False
        # 创建右击菜单
        self.menu = Menu(self)
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
        # 将信号连接到槽函数
        self.__connectSignalToSlot()

    def createSongCards(self):
        """ 创建歌曲卡 """
        for songInfo in self.playlist:
            self.appendOneSongCard(songInfo)
        if self.playlist:
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
            self.menu.moveUpAct.setEnabled(True)
            self.menu.moveDownAct.setEnabled(True)
            if self.currentRow() == len(self.playlist) - 1:
                self.menu.moveDownAct.setEnabled(False)
            if self.currentRow() == 0:
                self.menu.moveUpAct.setEnabled(False)
            self.menu.exec_(e.globalPos())

    def showSongPropertyDialog(self, songCard: SongCard = None):
        """ 显示属性面板 """
        songInfo = self.songCard_list[self.currentRow(
        )].songInfo if not songCard else songCard.songInfo
        w = SongPropertyDialog(songInfo, self.window())
        w.exec_()

    def removeSongCard(self, index):
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
                self.setCurrentIndex(index - 1)
            else:
                self.setCurrentIndex(index)
        # 发送信号
        self.removeItemSignal.emit(index)

    def setCurrentIndex(self, index: int):
        """ 设置当前播放歌曲下标，同时更新样式 """
        if not self.songCard_list or index==self.currentIndex:
            return
        # 将之前播放的歌曲卡的播放状态设置为False
        self.songCard_list[self.currentIndex].setPlay(False)
        # 更新当前播放歌曲下标
        self.currentIndex = index
        # 更新当前播放歌曲卡样式
        self.songCard_list[index].setPlay(True)

    def setPlaylist(self, playlist: list, isResetIndex: bool = True):
        """ 直接清空并更新播放列表 """
        self.playlist = playlist
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

    def updateSongCards(self, songInfo_list: list, isResetIndex: bool = True):
        """ 更新所有歌曲卡信息 """
        # 长度相等就更新信息，不相等就根据情况创建或者删除item
        if self.songCard_list:
            self.songCard_list[self.currentIndex].setPlay(False)
        deltaLen = len(songInfo_list) - len(self.playlist)
        oldSongInfoLen = len(self.playlist)
        if deltaLen > 0:
            # 添加item
            for songInfo in songInfo_list[oldSongInfoLen:]:
                self.appendOneSongCard(songInfo)
                QApplication.processEvents()
        elif deltaLen < 0:
            # 删除多余的item
            for i in range(
                len(self.playlist) - 1, len(self.playlist) + deltaLen - 1, -1
            ):
                self.item_list.pop()
                songCard = self.songCard_list.pop()
                songCard.deleteLater()
                self.takeItem(i)
        # 更新部分歌曲卡
        self.playlist = songInfo_list
        iterRange = (
            range(len(self.playlist) - deltaLen)
            if deltaLen > 0
            else range(len(self.playlist))
        )
        for i in iterRange:
            songInfo_dict = self.playlist[i]
            self.songCard_list[i].updateSongCard(songInfo_dict)
        # 更新样式和当前下标
        self.currentIndex = 0 if isResetIndex else self.currentIndex
        self.songCard_list[self.currentIndex].setPlay(True)

    def __switchToAlbumInterface(self, albumName: str, songerName: str):
        """ 切换到专辑界面 """
        self.switchToAlbumInterfaceSig.emit(albumName, songerName)

    def updateOneSongCard(self, oldSongInfo: dict, newSongInfo: dict):
        """ 更新一个歌曲卡 """
        if oldSongInfo in self.playlist:
            index = self.playlist.index(oldSongInfo)
            self.playlist[index] = newSongInfo.copy()
            self.songCard_list[index].updateSongCard(newSongInfo)

    def updateMultiSongCards(self, oldSongInfo_list: list, newSongInfo_list: list):
        """ 更新多个的歌曲卡 """
        for oldSongInfo, newSongInfo in zip(oldSongInfo_list, newSongInfo_list):
            self.updateOneSongCard(oldSongInfo, newSongInfo)

    def appendOneSongCard(self, songInfo: dict):
        """ 在歌曲列表视图尾部添加一个歌曲卡 """
        # 创建item和歌曲卡
        item = QListWidgetItem()
        songCard = SongCard(songInfo)
        # 记录下标
        songCard.itemIndex = len(self.songCard_list)
        songCard.resize(1150, 60)
        item.setSizeHint(QSize(songCard.width(), 60))
        self.addItem(item)
        # 将项目的内容重置为自定义类
        self.setItemWidget(item, songCard)
        # 将item和songCard添加到列表中
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
        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            # 所有歌曲卡进入选择模式
            self.__setAllSongCardSelectionModeOpen(True)
            # 发送信号要求显示状态状态栏
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
            songCard.songerLabel.setCursor(cursor)

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

    def __connectSignalToSlot(self):
        """ 将信号连接到槽函数 """
        # 右击菜单信号连接到槽函数
        self.menu.playAct.triggered.connect(
            lambda: self.__emitCurrentChangedSignal(self.currentRow()))
        self.menu.propertyAct.triggered.connect(self.showSongPropertyDialog)
        self.menu.removeAct.triggered.connect(
            lambda: self.removeSongCard(self.currentRow()))
        self.menu.showAlbumAct.triggered.connect(
            lambda: self.__switchToAlbumInterface(
                self.songCard_list[self.currentRow()].album,
                self.songCard_list[self.currentRow()].songer,
            )
        )
