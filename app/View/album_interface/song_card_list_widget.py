# coding:utf-8

from PyQt5.QtCore import Qt, pyqtSignal, QMargins
from PyQt5.QtGui import QContextMenuEvent

from app.components.song_list_widget.basic_song_list_widget import BasicSongListWidget
from app.components.song_list_widget.song_card_type import SongCardType

from .song_card_list_context_menu import SongCardListContextMenu


class SongCardListWidget(BasicSongListWidget):
    """ 专辑界面歌曲卡列表视图 """

    playSignal = pyqtSignal(int)
    playOneSongSig = pyqtSignal(dict)
    nextToPlayOneSongSig = pyqtSignal(dict)  # 插入一首歌到播放列表中

    def __init__(self, songInfo_list: list, parent=None):
        super().__init__(
            songInfo_list,
            SongCardType.ALBUM_INTERFACE_SONG_CARD,
            parent,
            QMargins(30, 430, 30, 0),
        )
        # 创建歌曲卡
        self.__createSongCards()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setAlternatingRowColors(True)
        # 设置层叠样式
        self.__setQss()

    def __createSongCards(self):
        """ 清空列表并创建新歌曲卡 """
        super().createSongCards(self.__connectSongCardSignalToSlot)

    def __playButtonSlot(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(index)
        self.setCurrentIndex(index)
        self.setPlay(index)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            contextMenu = SongCardListContextMenu(self)
            self.__connectMenuSignalToSlot(contextMenu)
            contextMenu.exec(self.cursor().pos())

    def __emitCurrentChangedSignal(self, index):
        """ 发送当前播放的歌曲卡变化信号，同时更新样式和歌曲信息卡 """
        if self.isInSelectionMode:
            return
        self.setPlay(index)
        # 发送歌曲信息更新信号
        self.playSignal.emit(index)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(
            "app\\resource\\css\\songTabInterfaceSongListWidget.qss", encoding="utf-8"
        ) as f:
            self.setStyleSheet(f.read())

    def updateAllSongCards(self, songInfo_list: list):
        """ 更新所有歌曲卡，根据给定的信息决定创建或者删除歌曲卡 """
        super().updateAllSongCards(songInfo_list, self.__connectSongCardSignalToSlot)

    def resizeEvent(self, e):
        """ 调整尺寸的同时调整滚动条的位置和尺寸 """
        super().resizeEvent(e)
        self.verticalScrollBar().move(-1, 40)
        self.verticalScrollBar().resize(
            self.verticalScrollBar().width(), self.height() - 156
        )

    def sortSongCardByTrackNum(self):
        """ 以曲序为基准排序歌曲卡 """
        self.sortSongInfo(key="tracknumber")
        self.updateAllSongCards(self.songInfo_list)

    def __connectMenuSignalToSlot(self, contextMenu: SongCardListContextMenu):
        """ 信号连接到槽 """
        contextMenu.playAct.triggered.connect(
            lambda: self.playOneSongSig.emit(
                self.songCard_list[self.currentRow()].songInfo
            )
        )
        contextMenu.nextSongAct.triggered.connect(
            lambda: self.nextToPlayOneSongSig.emit(
                self.songCard_list[self.currentRow()].songInfo
            )
        )
        contextMenu.editInfoAct.triggered.connect(self.showSongInfoEditPanel)
        contextMenu.showPropertyAct.triggered.connect(self.showPropertyPanel)
        contextMenu.deleteAct.triggered.connect(
            lambda: self.__removeSongCard(self.currentRow())
        )
        contextMenu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongToPlayingSignal.emit(
                self.songCard_list[self.currentRow()].songInfo
            )
        )
        contextMenu.selectAct.triggered.connect(
            lambda: self.songCard_list[self.currentRow()].setChecked(True)
        )
        contextMenu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.songInfo_list)
        )
        contextMenu.addToMenu.newPlayList.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(
                [self.songCard_list[self.currentRow()].songInfo]
            )
        )

    def __connectSongCardSignalToSlot(self, songCard):
        """ 将歌曲卡信号连接到槽 """
        songCard.doubleClicked.connect(self.__emitCurrentChangedSignal)
        songCard.playButtonClicked.connect(self.__playButtonSlot)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.checkedStateChanged.connect(self.songCardCheckedStateChangedSlot)
