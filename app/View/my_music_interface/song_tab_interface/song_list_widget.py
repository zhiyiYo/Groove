# coding:utf-8
from components.dialog_box.message_dialog import MessageDialog
from components.menu import AddToMenu, DWMMenu
from components.song_list_widget import BasicSongListWidget, SongCardType
from PyQt5.QtCore import QFile, QMargins, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction, QLabel


class SongListWidget(BasicSongListWidget):
    """ 歌曲卡列表视图 """

    playSignal = pyqtSignal(dict)                       # 播放选中的歌曲
    playOneSongSig = pyqtSignal(dict)                   # 重置播放列表为指定的一首歌
    nextToPlayOneSongSig = pyqtSignal(dict)             # 下一首播放
    switchToSingerInterfaceSig = pyqtSignal(str)        # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)    # 切换到专辑界面

    def __init__(self, songInfo_list: list, parent=None):
        """
        Parameters
        ----------
        songInfo_list:list
            歌曲信息列表

        parent:
            父级窗口
        """
        super().__init__(
            songInfo_list,
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
        self.guideLabel.setHidden(bool(self.songInfo_list))

    def __playButtonSlot(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(self.songCard_list[index].songInfo)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            contextMenu = SongCardListContextMenu(self)
            self.__connectMenuSignalToSlot(contextMenu)
            contextMenu.exec(self.cursor().pos())

    def __onSongCardDoubleClicked(self, index):
        """ 发送当前播放的歌曲卡变化信号，同时更新样式和歌曲信息卡 """
        # 处于选择模式时不发送信号
        if self.isInSelectionMode:
            return
        # 发送歌曲信息更新信号
        self.playSignal.emit(self.songCard_list[index].songInfo)

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
        key = {"Date added": "createTime",
               "A to Z": "songName", "Artist": "singer"}[sortMode]
        songInfo_list = self.sortSongInfo(key)

        self.updateAllSongCards(songInfo_list)
        if self.playingSongInfo in self.songInfo_list:
            self.setPlay(self.songInfo_list.index(self.playingSongInfo))

    def updateAllSongCards(self, songInfo_list: list):
        """ 更新所有歌曲卡，根据给定的信息决定创建或者删除歌曲卡 """
        super().updateAllSongCards(songInfo_list)
        self.guideLabel.setHidden(bool(self.songInfo_list))

    def __showDeleteCardDialog(self):
        index = self.currentRow()
        songInfo = self.songInfo_list[index]

        name = songInfo['songName']
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{name}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.removeSongCard(index))
        w.yesSignal.connect(
            lambda: self.removeSongSignal.emit(songInfo["songPath"]))
        w.exec_()

    def __connectMenuSignalToSlot(self, menu):
        """ 信号连接到槽 """
        menu.playAct.triggered.connect(
            lambda: self.playOneSongSig.emit(
                self.songCard_list[self.currentRow()].songInfo))
        menu.nextSongAct.triggered.connect(
            lambda: self.nextToPlayOneSongSig.emit(
                self.songCard_list[self.currentRow()].songInfo))
        # 显示歌曲信息编辑面板
        menu.editInfoAct.triggered.connect(self.showSongInfoEditDialog)
        # 显示属性面板
        menu.showPropertyAct.triggered.connect(
            self.showSongPropertyDialog)
        # 显示专辑界面
        menu.showAlbumAct.triggered.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(
                self.songCard_list[self.currentRow()].album,
                self.songCard_list[self.currentRow()].singer,
            )
        )
        # 删除歌曲卡
        menu.deleteAct.triggered.connect(self.__showDeleteCardDialog)
        # 将歌曲添加到正在播放列表
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongToPlayingSignal.emit(
                self.songCard_list[self.currentRow()].songInfo))
        # 进入选择模式
        menu.selectAct.triggered.connect(
            lambda: self.songCard_list[self.currentRow()].setChecked(True))
        # 将歌曲添加到已存在的自定义播放列表中
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(
                name, [self.songCard_list[self.currentRow()].songInfo]))
        # 将歌曲添加到新建的播放列表
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(
                [self.songCard_list[self.currentRow()].songInfo]))

    def _connectSongCardSignalToSlot(self, songCard):
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


class SongCardListContextMenu(DWMMenu):
    """ 歌曲卡列表右击菜单 """

    def __init__(self, parent):
        super().__init__("", parent)
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
