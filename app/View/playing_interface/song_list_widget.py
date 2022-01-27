# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from components.dialog_box.song_property_dialog import SongPropertyDialog
from components.widgets.list_widget import ListWidget
from PyQt5.QtCore import QFile, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QApplication, QListWidgetItem

from .menu import Menu
from .song_card import SongCard


class SongListWidget(ListWidget):
    """ 正在播放列表 """

    emptyChanged = pyqtSignal(bool)                      # 歌曲列表 空/非空 变化
    removeSongSig = pyqtSignal(int)                      # 移除歌曲
    currentIndexChanged = pyqtSignal(int)                # 当前播放的变化
    isAllCheckedChanged = pyqtSignal(bool)               # 歌曲卡卡全部选中改变
    selectionModeStateChanged = pyqtSignal(bool)         # 进入或退出选择模式
    checkedSongCardNumChanged = pyqtSignal(int)          # 选中的歌曲卡数量改变
    switchToSingerInterfaceSig = pyqtSignal(str)         # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)     # 切换到专辑界面
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 将歌曲添加到新的自定义播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 将歌曲添加到已存在的自定义播放列表

    def __init__(self, songInfos: List[SongInfo], parent=None):
        super().__init__(parent)
        self.songInfos = songInfos
        self.currentIndex = 0
        self.item_list = []
        self.songCards = []  # type:List[SongCard]
        self.checkedSongCards = []  # type:List[SongCard]
        self.isInSelectionMode = False
        self.isAllSongCardsChecked = False
        self.createSongCards()
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1150 + 60, 800)
        self.setViewportMargins(30, 0, 30, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__setQss()

    def createSongCards(self):
        """ 创建歌曲卡 """
        for songInfo in self.songInfos:
            self.appendOneSongCard(songInfo)
            QApplication.processEvents()

        if self.songInfos:
            self.songCards[self.currentIndex].setPlay(True)

        self.resize(1200, 800)

    def __setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/playing_interface_song_list_widget.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def resizeEvent(self, e):
        """ 更新item的尺寸 """
        for item in self.item_list:
            item.setSizeHint(QSize(self.width() - 60, 60))

        super().resizeEvent(e)

    def __emitCurrentChangedSignal(self, index):
        """ 发送当前播放的歌曲卡下标变化信号，同时更新样式和歌曲信息卡 """
        self.currentIndexChanged.emit(index)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 显示右击菜单 """
        hitIndex = self.indexAt(e.pos()).column()
        if hitIndex > -1:
            menu = Menu(self)
            self.__connectContextMenuSignalToSlot(menu)
            if self.currentRow() == len(self.songInfos) - 1:
                menu.moveDownAct.setEnabled(False)
            if self.currentRow() == 0:
                menu.moveUpAct.setEnabled(False)
            menu.exec_(e.globalPos())

    def showSongPropertyDialog(self, songCard: SongCard = None):
        """ 显示属性面板 """
        songInfo = self.songCards[self.currentRow(
        )].songInfo if not songCard else songCard.songInfo
        w = SongPropertyDialog(songInfo, self.window())
        w.exec_()

    def removeSongCard(self, index):
        """ 移除选一个歌曲卡 """
        # 更新下标
        for songCard in self.songCards[index+1:]:
            songCard.itemIndex -= 1

        # 更新歌曲卡选中状态
        if self.currentIndex > index:
            self.currentIndex -= 1
        elif self.currentIndex == index:
            self.setCurrentIndex(index-1)

        # 删除歌曲卡
        self.songInfos.pop(index)
        songCard = self.songCards.pop(index)
        songCard.deleteLater()
        self.item_list.pop(index)
        self.takeItem(index)

        # 发送信号
        self.removeSongSig.emit(index)

    def setCurrentIndex(self, index: int):
        """ 设置当前播放歌曲下标，同时更新样式 """
        if not self.songCards or index == self.currentIndex:
            return

        # 将之前播放的歌曲卡的播放状态设置为False
        self.songCards[self.currentIndex].setPlay(False)

        # 更新当前播放歌曲下标
        self.currentIndex = index

        # 更新当前播放歌曲卡样式
        self.songCards[index].setPlay(True)

    def setPlaylist(self, playlist: list, isResetIndex: bool = True):
        """ 直接清空并更新播放列表 """
        self.songInfos = playlist
        self.clearSongCards(isResetIndex)
        self.createSongCards()

    def clearSongCards(self, isResetIndex: bool = True):
        """ 清空歌曲卡 """
        self.item_list.clear()
        self.clear()
        # 释放内存
        for songCard in self.songCards:
            songCard.deleteLater()
        self.songCards.clear()
        self.currentIndex = 0 if isResetIndex else self.currentIndex

    def updateSongCards(self, songInfos: list, isResetIndex=True, index=0):
        """ 更新所有歌曲卡信息 """
        # 长度相等就更新信息，不相等就根据情况创建或者删除item
        if self.songCards:
            self.songCards[self.currentIndex].setPlay(False)

        N = len(songInfos)
        N_ = len(self.songCards)    # 必须用 songCards，因为 songInfos 是引用

        # 添加item
        if N > N_:
            for songInfo in songInfos[N_:]:
                self.appendOneSongCard(songInfo)
                QApplication.processEvents()
        # 删除多余的item
        elif N < N_:
            for i in range(N_ - 1, N - 1, -1):
                self.item_list.pop()
                songCard = self.songCards.pop()
                songCard.deleteLater()
                self.takeItem(i)
                QApplication.processEvents()

        # 更新部分歌曲卡
        self.songInfos = songInfos

        for i in range(min(N_, N)):
            songInfo = self.songInfos[i]
            self.songCards[i].updateSongCard(songInfo)
            QApplication.processEvents()

        # 更新样式和当前下标
        self.currentIndex = index if isResetIndex else self.currentIndex
        if self.songInfos:
            self.songCards[self.currentIndex].setPlay(True)

    def updateOneSongCard(self, newSongInfo: SongInfo):
        """ 更新一个歌曲卡 """
        for i, songInfo in enumerate(self.songInfos):
            if songInfo.file == newSongInfo.file:
                self.songInfos[i] = newSongInfo
                self.songCards[i].updateSongCard(newSongInfo)

    def updateMultiSongCards(self, songInfos: List[SongInfo]):
        """ 更新多个的歌曲卡 """
        for songInfo in songInfos:
            self.updateOneSongCard(songInfo)

    def appendOneSongCard(self, songInfo: SongInfo):
        """ 在歌曲列表视图尾部添加一个歌曲卡 """
        songCard = SongCard(songInfo)
        songCard.itemIndex = len(self.songCards)
        songCard.resize(self.width()-60, 60)

        item = QListWidgetItem()
        item.setSizeHint(QSize(songCard.width(), 60))
        self.addItem(item)
        self.setItemWidget(item, songCard)

        self.songCards.append(songCard)
        self.item_list.append(item)

        # 信号连接到槽
        songCard.aniStartSig.connect(
            lambda: self.songCards[self.currentIndex].setPlay(False))
        songCard.clicked.connect(self.__emitCurrentChangedSignal)
        songCard.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)
        songCard.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        songCard.addSongToCustomPlaylistSig.connect(
            lambda name, songInfo: self.addSongsToCustomPlaylistSig.emit(name, [songInfo]))
        songCard.addSongToNewCustomPlaylistSig.connect(
            lambda songInfo: self.addSongsToNewCustomPlaylistSig.emit([songInfo]))
        songCard.checkedStateChanged.connect(self.onCheckedStateChanged)

    def onCheckedStateChanged(self, index: int, isChecked: bool):
        """ 歌曲卡选中状态改变对应槽函数 """
        songCard = self.songCards[index]

        # 如果歌曲卡不在选中的歌曲列表中且该歌曲卡变为选中状态就将其添加到列表中
        if songCard not in self.checkedSongCards and isChecked:
            self.checkedSongCards.append(songCard)
            self.checkedSongCardNumChanged.emit(len(self.checkedSongCards))
        # 如果歌曲卡已经在列表中且该歌曲卡变为非选中状态就弹出该歌曲卡
        elif songCard in self.checkedSongCards and not isChecked:
            self.checkedSongCards.remove(songCard)
            self.checkedSongCardNumChanged.emit(len(self.checkedSongCards))

        isAllChecked = (len(self.checkedSongCards)
                        == len(self.songCards))
        if isAllChecked != self.isAllSongCardsChecked:
            self.isAllSongCardsChecked = isAllChecked
            self.isAllCheckedChanged.emit(isAllChecked)

        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            # 所有歌曲卡进入选择模式
            self.__setAllSongCardSelectionModeOpen(True)
            self.selectionModeStateChanged.emit(True)
            self.isInSelectionMode = True
        elif not self.checkedSongCards:
            # 所有歌曲卡退出选择模式
            self.__setAllSongCardSelectionModeOpen(False)
            # 发送信号要求隐藏状态状态栏
            self.selectionModeStateChanged.emit(False)
            self.isInSelectionMode = False

    def __setAllSongCardSelectionModeOpen(self, isOpen: bool):
        """ 设置所有歌曲卡是否进入选择模式 """
        cursor = Qt.ArrowCursor if isOpen else Qt.PointingHandCursor
        for songCard in self.songCards:
            songCard.setSelectionModeOpen(isOpen)
            songCard.albumLabel.setCursor(cursor)
            songCard.singerLabel.setCursor(cursor)

    def setAllSongCardCheckedState(self, isAllChecked: bool):
        """ 设置所有的歌曲卡checked状态 """
        if self.isAllSongCardsChecked == isAllChecked:
            return

        self.isAllSongCardsChecked = isAllChecked
        for songCard in self.songCards:
            songCard.setChecked(isAllChecked)

    def unCheckAllSongCards(self):
        """ 取消所有歌曲卡选中状态 """
        for songCard in self.songCards:
            songCard.setChecked(False)

    def __connectContextMenuSignalToSlot(self, menu: Menu):
        """ 将信号连接到槽函数 """
        # 右击菜单信号连接到槽函数
        menu.playAct.triggered.connect(
            lambda: self.__emitCurrentChangedSignal(self.currentRow()))
        menu.propertyAct.triggered.connect(self.showSongPropertyDialog)
        menu.removeAct.triggered.connect(
            lambda: self.removeSongCard(self.currentRow()))
        menu.selectAct.triggered.connect(
            lambda: self.songCards[self.currentRow()].setChecked(True))
        menu.showAlbumAct.triggered.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(
                self.songCards[self.currentRow()].singer,
                self.songCards[self.currentRow()].album))

        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(
                name, [self.songInfos[self.currentRow()]]))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(
                [self.songInfos[self.currentRow()]]))
