# coding:utf-8

from app.components.song_list_widget.basic_song_list_widget import BasicSongListWidget
from app.components.song_list_widget.song_card_type import SongCardType
from PyQt5.QtCore import QMargins, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent

from .song_card_list_context_menu import SongCardListContextMenu


class SongCardListWidget(BasicSongListWidget):
    """ 定义一个歌曲卡列表视图 """

    playSignal = pyqtSignal(dict)  # 将播放列表的当前歌曲切换为指定的歌曲卡
    playOneSongSig = pyqtSignal(dict)  # 重置播放列表为指定的一首歌
    nextToPlayOneSongSig = pyqtSignal(dict)
    switchToAlbumInterfaceSig = pyqtSignal(str, str)

    def __init__(self, songInfo_list: list, parent=None):
        super().__init__(
            songInfo_list,
            SongCardType.SONG_TAB_SONG_CARD,
            parent,
            QMargins(30, 245, 30, 0),
        )
        self.resize(1150, 758)
        self.sortMode = "添加时间"
        # 创建歌曲卡
        self.__createSongCards()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置层叠样式
        self.__setQss()

    def __createSongCards(self):
        """ 清空列表并创建新歌曲卡 """
        super().createSongCards(self.__connectSongCardSignalToSlot)

    def __playButtonSlot(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(self.songCard_list[index].songInfo)
        self.setCurrentIndex(index)
        # self.setPlay(index)

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
        # 处于选择模式时不发送信号
        if self.isInSelectionMode:
            return
        # self.setPlay(index)
        # 发送歌曲信息更新信号
        self.playSignal.emit(self.songCard_list[index].songInfo)

    def __setQss(self):
        """ 设置层叠样式 """
        with open("app/resource/css/songTabInterfaceSongListWidget.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def setSortMode(self, sortMode: str):
        """ 根据当前的排序模式来排序歌曲卡

        Parameters
        ----------
        sortMode: str
            排序方式，有 `添加时间`、`A到Z` 和 `歌手` 三种
        """
        self.sortMode = sortMode
        if self.sortMode == "添加时间":
            self.sortSongInfo("createTime")
        elif self.sortMode == "A到Z":
            self.sortSongInfo("songName")
        elif self.sortMode == "歌手":
            self.sortSongInfo("songer")
        self.updateAllSongCards(self.songInfo_list)
        if self.playingSongInfo in self.songInfo_list:
            self.setPlay(self.songInfo_list.index(self.playingSongInfo))

    def updateAllSongCards(self, songInfo_list: list):
        """ 更新所有歌曲卡，根据给定的信息决定创建或者删除歌曲卡 """
        super().updateAllSongCards(songInfo_list, self.__connectSongCardSignalToSlot)

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
        # 显示歌曲信息编辑面板
        contextMenu.editInfoAct.triggered.connect(self.showSongInfoEditDialog)
        # 显示属性面板
        contextMenu.showPropertyAct.triggered.connect(
            self.showSongPropertyDialog)
        # 显示专辑界面
        contextMenu.showAlbumAct.triggered.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(
                self.songCard_list[self.currentRow()].album,
                self.songCard_list[self.currentRow()].songer,
            )
        )
        # 删除歌曲卡
        contextMenu.deleteAct.triggered.connect(
            lambda: self.removeSongCard(self.currentRow())
        )
        # 将歌曲添加到正在播放列表
        contextMenu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongToPlayingSignal.emit(
                self.songCard_list[self.currentRow()].songInfo
            )
        )
        # 进入选择模式
        contextMenu.selectAct.triggered.connect(
            lambda: self.songCard_list[self.currentRow()].setChecked(True)
        )
        # 将歌曲添加到已存在的自定义播放列表中
        contextMenu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(
                name, [self.songCard_list[self.currentRow()].songInfo]
            )
        )
        # 将歌曲添加到新建的播放列表
        contextMenu.addToMenu.newPlayList.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(
                [self.songCard_list[self.currentRow()].songInfo]
            )
        )

    def __connectSongCardSignalToSlot(self, songCard):
        """ 将歌曲卡信号连接到槽 """
        songCard.addSongToPlayingSig.connect(self.addSongToPlayingSignal)
        songCard.doubleClicked.connect(self.__emitCurrentChangedSignal)
        songCard.playButtonClicked.connect(self.__playButtonSlot)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        songCard.checkedStateChanged.connect(
            self.songCardCheckedStateChangedSlot)
        songCard.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
