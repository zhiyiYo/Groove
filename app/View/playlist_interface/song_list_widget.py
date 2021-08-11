# coding:utf-8
from app.components.menu import AddToMenu, DWMMenu
from app.components.song_list_widget.basic_song_list_widget import BasicSongListWidget
from app.components.song_list_widget.song_card_type import SongCardType
from PyQt5.QtCore import QMargins, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction


class SongListWidget(BasicSongListWidget):
    """ 歌曲卡列表视图 """

    playSignal = pyqtSignal(int)       # 将播放列表的当前歌曲切换为指定的歌曲卡
    playOneSongSig = pyqtSignal(dict)   # 只播放一首歌
    nextToPlayOneSongSig = pyqtSignal(dict)
    switchToAlbumInterfaceSig = pyqtSignal(str, str)

    def __init__(self, songInfo_list: list, parent):
        super().__init__(songInfo_list, SongCardType.PLAYLIST_INTERFACE_SONG_CARD,
                         parent, QMargins(30, 0, 30, 0), 0)
        self.resize(1150, 758)
        self.createSongCards(self.__connectSongCardSignalToSlot)
        self.setAlternatingRowColors(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__setQss()

    def appendOneSongCard(self, songInfo: dict, connectSongCardSigToSlotFunc):
        super().appendOneSongCard(songInfo, connectSongCardSigToSlotFunc)
        self.__adjustHeight()

    def removeSongCard(self, index):
        super().removeSongCard(index)
        self.__adjustHeight()

    def clearSongCards(self):
        super().clearSongCards()
        self.__adjustHeight()

    def updateAllSongCards(self, songInfo_list: list):
        """ 更新所有歌曲卡 """
        super().updateAllSongCards(songInfo_list, self.__connectSongCardSignalToSlot)
        self.__adjustHeight()

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            contextMenu = SongCardListContextMenu(self)
            self.__connectMenuSignalToSlot(contextMenu)
            contextMenu.exec(self.cursor().pos())

    def __setQss(self):
        """ 设置层叠样式 """
        with open("app/resource/css/playlist_interface_song_list_widget.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def __onPlayButtonClicked(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(index)
        self.setCurrentIndex(index)
        self.setPlay(index)

    def __onSongCardDoubleClicked(self, index):
        """ 发送当前播放的歌曲卡变化信号，同时更新样式和歌曲信息卡 """
        if self.isInSelectionMode:
            return
        self.playSignal.emit(index)

    def __onRemoveButtonClicked(self, index):
        """ 移除歌曲卡按钮点击槽函数 """
        path = self.sender().songPath
        self.removeSongCard(index)
        self.removeSongSignal.emit(path)

    def __adjustHeight(self):
        """ 调整高度 """
        margin = self.viewportMargins()
        self.resize(self.width(), 60*len(self.songCard_list) +
                    margin.bottom()+margin.top()+116)

    def wheelEvent(self, e):
        return

    def __connectSongCardSignalToSlot(self, songCard):
        """ 将歌曲卡信号连接到槽 """
        songCard.doubleClicked.connect(self.__onSongCardDoubleClicked)
        songCard.removeSongSignal.connect(self.__onRemoveButtonClicked)
        songCard.playButtonClicked.connect(self.__onPlayButtonClicked)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.checkedStateChanged.connect(
            self.onSongCardCheckedStateChanged)
        songCard.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)

    def __connectMenuSignalToSlot(self, contextMenu):
        """ 右击菜单信号连接到槽 """
        contextMenu.playAct.triggered.connect(
            lambda: self.playOneSongSig.emit(
                self.songCard_list[self.currentRow()].songInfo))
        contextMenu.nextSongAct.triggered.connect(
            lambda: self.nextToPlayOneSongSig.emit(
                self.songCard_list[self.currentRow()].songInfo))
        contextMenu.editInfoAct.triggered.connect(self.showSongInfoEditDialog)
        contextMenu.showPropertyAct.triggered.connect(
            self.showSongPropertyDialog)
        contextMenu.deleteAct.triggered.connect(
            lambda: self.__onRemoveButtonClicked(self.currentRow()))
        contextMenu.selectAct.triggered.connect(
            lambda: self.songCard_list[self.currentRow()].setChecked(True))
        contextMenu.showAlbumAct.triggered.connect(lambda: self.switchToAlbumInterfaceSig.emit(
            self.songCard_list[self.currentRow()].album,
            self.songCard_list[self.currentRow()].songer))

        contextMenu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongToPlayingSignal.emit(
                self.songCard_list[self.currentRow()].songInfo))
        contextMenu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(
                name, self.songInfo_list))
        contextMenu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(
                [self.songCard_list[self.currentRow()].songInfo]))


class SongCardListContextMenu(DWMMenu):
    """ 歌曲卡列表右击菜单 """

    def __init__(self, parent):
        super().__init__("", parent)
        # 创建主菜单动作
        self.playAct = QAction("播放", self)
        self.nextSongAct = QAction("下一首播放", self)
        self.deleteAct = QAction("从播放列表中删除", self)
        self.showAlbumAct = QAction("显示专辑", self)
        self.editInfoAct = QAction("编辑信息", self)
        self.showPropertyAct = QAction("属性", self)
        self.selectAct = QAction("选择", self)
        # 创建菜单和子菜单
        self.addToMenu = AddToMenu("添加到", self)
        # 将动作添加到菜单中
        self.addActions([self.playAct, self.nextSongAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        # 将其余动作添加到主菜单
        self.addActions([self.deleteAct, self.showAlbumAct,
                        self.editInfoAct, self.showPropertyAct])
        self.addSeparator()
        self.addAction(self.selectAct)
