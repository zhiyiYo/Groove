# coding:utf-8
from typing import List
from common.database.entity import SongInfo

from components.dialog_box.message_dialog import MessageDialog
from components.widgets.menu import AddToMenu, DWMMenu
from components.song_list_widget import BasicSongListWidget, SongCardType
from components.song_list_widget.song_card import SongTabSongCard
from PyQt5.QtCore import QFile, QMargins, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction, QLabel


class SongCardListContextMenu(DWMMenu):
    """ 歌曲卡列表右击菜单 """

    def __init__(self, parent):
        super().__init__(parent=parent)
        # 创建主菜单动作
        self.playAct = QAction(self.tr("Play"), self)
        self.nextSongAct = QAction(self.tr("Play next"), self)
        self.showAlbumAct = QAction(self.tr("Show album"), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.showPropertyAct = QAction(self.tr("Properties"), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        # 创建菜单和子菜单
        self.addToMenu = AddToMenu(self.tr('Add to'), self)
        # 将动作添加到菜单中
        self.addActions([self.playAct, self.nextSongAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        # 将其余动作添加到主菜单
        self.addActions(
            [self.showAlbumAct, self.editInfoAct, self.showPropertyAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)


class SongListWidget(BasicSongListWidget):
    """ 歌曲卡列表视图 """

    playSignal = pyqtSignal(SongInfo)                   # 播放选中的歌曲
    playOneSongSig = pyqtSignal(SongInfo)               # 重置播放列表为指定的一首歌
    nextToPlayOneSongSig = pyqtSignal(SongInfo)         # 下一首播放
    switchToSingerInterfaceSig = pyqtSignal(str)        # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)    # 切换到专辑界面

    def __init__(self, songInfos: List[SongInfo], parent=None):
        """
        Parameters
        ----------
        songInfos: List[SongInfo]
            歌曲信息列表

        parent:
            父级窗口
        """
        super().__init__(
            songInfos,
            SongCardType.SONG_TAB_SONG_CARD,
            parent,
            QMargins(30, 245, 30, 0),
        )
        self.resize(1150, 758)
        self.sortMode = "createTime"

        # 创建歌曲卡
        self.createSongCards()
        self.guideLabel = QLabel(
            self.tr("There is nothing to display here. Try a different filter."), self)

        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置层叠样式
        self.__setQss()
        self.guideLabel.move(35, 286)
        self.guideLabel.setHidden(bool(self.songInfos))

    def __playButtonSlot(self, index: int):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(self.songCards[index].songInfo)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            contextMenu = SongCardListContextMenu(self)
            self.__connectMenuSignalToSlot(contextMenu)
            contextMenu.exec(self.cursor().pos())

    def __onSongCardDoubleClicked(self, index: int):
        """ 发送当前播放的歌曲卡变化信号，同时更新样式和歌曲信息卡 """
        if self.isInSelectionMode:
            return

        # 发送歌曲信息更新信号
        self.playSignal.emit(self.songCards[index].songInfo)

    def __setQss(self):
        """ 设置层叠样式 """
        self.guideLabel.setObjectName('guideLabel')
        f = QFile(":/qss/song_tab_interface_song_list_widget.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()
        self.guideLabel.adjustSize()

    def setSortMode(self, sortMode: str):
        """ 根据当前的排序模式来排序歌曲卡

        Parameters
        ----------
        sortMode: str
            排序方式，有 `Date added`、`A to Z` 和 `Artist` 三种
        """
        if self.sortMode == sortMode:
            return

        self.sortMode = sortMode
        key = {
            "Date added": "createTime",
            "A to Z": "title",
            "Artist": "singer"
        }[sortMode]
        songInfos = self.sortSongInfo(key)
        self.updateAllSongCards(songInfos)

        if self.playingSongInfo in self.songInfos:
            self.setPlay(self.songInfos.index(self.playingSongInfo))

    def updateAllSongCards(self, songInfos: List[SongInfo]):
        """ 更新所有歌曲卡，根据给定的信息决定创建或者删除歌曲卡 """
        super().updateAllSongCards(songInfos)
        self.guideLabel.setHidden(bool(self.songInfos))

    def __showDeleteCardDialog(self):
        index = self.currentRow()
        songInfo = self.songInfos[index]

        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{songInfo.title}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.removeSongCard(index))
        w.yesSignal.connect(
            lambda: self.removeSongSignal.emit(songInfo.file))
        w.exec_()

    def __connectMenuSignalToSlot(self, menu: SongCardListContextMenu):
        """ 信号连接到槽 """
        menu.playAct.triggered.connect(
            lambda: self.playOneSongSig.emit(self.songCards[self.currentRow()].songInfo))

        menu.nextSongAct.triggered.connect(
            lambda: self.nextToPlayOneSongSig.emit(self.songCards[self.currentRow()].songInfo))

        # 显示歌曲信息编辑面板
        menu.editInfoAct.triggered.connect(self.showSongInfoEditDialog)

        # 显示属性面板
        menu.showPropertyAct.triggered.connect(self.showSongPropertyDialog)

        # 显示专辑界面
        menu.showAlbumAct.triggered.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(
                self.songCards[self.currentRow()].singer,
                self.songCards[self.currentRow()].album,
            )
        )
        # 删除歌曲卡
        menu.deleteAct.triggered.connect(self.__showDeleteCardDialog)

        # 将歌曲添加到正在播放列表
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongToPlayingSignal.emit(self.songCards[self.currentRow()].songInfo))

        # 进入选择模式
        menu.selectAct.triggered.connect(
            lambda: self.songCards[self.currentRow()].setChecked(True))

        # 将歌曲添加到已存在的自定义播放列表中
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(
                name, [self.songCards[self.currentRow()].songInfo]))

        # 将歌曲添加到新建的播放列表
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(
                [self.songCards[self.currentRow()].songInfo]))

    def _connectSongCardSignalToSlot(self, songCard: SongTabSongCard):
        """ 将歌曲卡信号连接到槽 """
        songCard.addSongToPlayingSig.connect(self.addSongToPlayingSignal)
        songCard.doubleClicked.connect(self.__onSongCardDoubleClicked)
        songCard.playButtonClicked.connect(self.__playButtonSlot)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)
        songCard.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        songCard.checkedStateChanged.connect(
            self.onSongCardCheckedStateChanged)
        songCard.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        songCard.addSongToNewCustomPlaylistSig.connect(
            lambda songInfo: self.addSongsToNewCustomPlaylistSig.emit([songInfo]))
