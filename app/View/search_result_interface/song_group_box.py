# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from common.signal_bus import signalBus
from components.buttons.three_state_button import ThreeStatePushButton
from components.song_list_widget import NoScrollSongListWidget, SongCardType
from components.song_list_widget.song_card import (NoCheckBoxSongCard,
                                                   OnlineSongCard)
from components.widgets.label import ClickableLabel
from components.widgets.menu import AddToMenu, DownloadMenu, DWMMenu
from PyQt5.QtCore import QFile, QMargins, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction, QPushButton, QWidget


class SongGroupBox(QWidget):
    """ 歌曲分组框 """

    loadMoreSignal = pyqtSignal()
    switchToMoreSearchResultInterfaceSig = pyqtSignal()

    def __init__(self, song_type: str, parent=None):
        """
        Parameters
        ----------
        song_type: str
            歌曲类型，可以是 `'Online songs'` 或 `'Local songs'`

        parent:
            父级窗口
        """
        super().__init__(parent=parent)
        if song_type not in ['Online songs', 'Local songs']:
            raise ValueError("歌曲类型必须是 'Online songs' 或 'Local songs'")

        self.songType = song_type
        self.songInfos = []
        if song_type == 'Local songs':
            self.songListWidget = LocalSongListWidget(self)
            self.titleButton = QPushButton(self.tr('Local songs'), self)
            self.loadMoreLabel = ClickableLabel()
            self.loadMoreLabel.hide()   # 隐藏本地歌曲的加载更多标签
        else:
            self.songListWidget = OnlineSongListWidget(self)
            self.titleButton = QPushButton(self.tr('Online songs'), self)
            self.loadMoreLabel = ClickableLabel(self.tr("Load more"), self)

        self.showAllButton = ThreeStatePushButton(
            {
                "normal": ":/images/search_result_interface/ShowAll_normal.png",
                "hover": ":/images/search_result_interface/ShowAll_hover.png",
                "pressed": ":/images/search_result_interface/ShowAll_pressed.png",
            },
            self.tr(' Show All'),
            (14, 14),
            self,
        )
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1200, 500)
        self.setMinimumHeight(47)
        self.titleButton.move(35, 0)
        self.songListWidget.move(0, 57)
        self.loadMoreLabel.setCursor(Qt.PointingHandCursor)
        self.showAllButton.setHidden(self.songType == 'Online songs')
        self.titleButton.clicked.connect(self.__showMoreSearchResultInterface)
        self.showAllButton.clicked.connect(self.__showMoreSearchResultInterface)
        self.loadMoreLabel.clicked.connect(self.__onLoadMoreLabelClicked)
        self.__setQss()

    def __setQss(self):
        """ 设置层叠样式 """
        self.titleButton.setObjectName('titleButton')
        self.showAllButton.setObjectName('showAllButton')
        self.loadMoreLabel.setProperty("loadFinished", "false")

        f = QFile(":/qss/song_group_box.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.titleButton.adjustSize()
        self.showAllButton.adjustSize()

    def resizeEvent(self, e):
        self.songListWidget.resize(self.width(), self.songListWidget.height())
        self.showAllButton.move(self.width()-self.showAllButton.width()-30, 5)
        self.loadMoreLabel.move(self.width()//2-self.loadMoreLabel.width()//2,
                                57+self.songListWidget.height()+17)

    def __adjustHeight(self):
        """ 调节高度 """
        spacing = 0 if self.loadMoreLabel.isHidden() else 17*2+19
        self.setFixedHeight(57+self.songListWidget.height()+spacing)
        self.loadMoreLabel.move(self.loadMoreLabel.x(),
                                57+self.songListWidget.height()+17)

    def updateWindow(self, songInfos: List[SongInfo]):
        """ 更新窗口 """
        if songInfos == self.songInfos:
            return

        self.songInfos = songInfos
        self.songListWidget.updateAllSongCards(self.songInfos)
        self.__adjustHeight()

    def loadMoreOnlineMusic(self, songInfos: List[SongInfo]):
        """ 载入更多在线音乐

        Parameters
        ----------
        songInfos: List[SongInfo]
            新添加的歌曲信息列表
        """
        if self.songType != 'Online songs':
            raise Exception('歌曲类型不是在线音乐，无法载入更多')

        self.songInfos.extend(songInfos)
        self.songListWidget.songInfos = self.songInfos
        self.songListWidget.appendSongCards(songInfos)
        self.__adjustHeight()

    def __onLoadMoreLabelClicked(self):
        """ 加载更多 """
        if self.loadMoreLabel.isHidden() or self.loadMoreLabel.property("loadFinished") == "true":
            return

        self.loadMoreSignal.emit()

    def __showMoreSearchResultInterface(self):
        """ 显示更多搜索结果界面 """
        if self.songType == 'Online songs':
            return

        self.switchToMoreSearchResultInterfaceSig.emit()


class LocalSongListWidget(NoScrollSongListWidget):
    """ 本地音乐歌曲卡列表 """

    playSignal = pyqtSignal(int)                        # 将播放列表的当前歌曲切换为指定的歌曲卡

    def __init__(self, parent=None):
        """
        Parameters
        ----------
        parent:
            父级窗口
        """
        super().__init__(None, SongCardType.NO_CHECKBOX_SONG_CARD,
                         parent, QMargins(30, 0, 30, 0), 0)
        self.__setQss()

    def __onPlayButtonClicked(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(index)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            contextMenu = LocalSongListContextMenu(self)
            self.__connectContextMenuSignalToSlot(contextMenu)
            contextMenu.exec(self.cursor().pos())

    def __setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/song_tab_interface_song_list_widget.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def __connectContextMenuSignalToSlot(self, menu):
        """ 信号连接到槽 """
        menu.playAct.triggered.connect(
            lambda: signalBus.playOneSongCardSig.emit(self.currentSongInfo))
        menu.nextSongAct.triggered.connect(
            lambda: signalBus.nextToPlaySig.emit([self.currentSongInfo]))
        menu.showPropertyAct.triggered.connect(self.showSongPropertyDialog)
        menu.showAlbumAct.triggered.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(
                self.currentSongCard.singer,
                self.currentSongCard.album
            )
        )

        menu.addToMenu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit([self.currentSongInfo]))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, [self.currentSongInfo]))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.currentSongInfo]))

    def _connectSongCardSignalToSlot(self, songCard: NoCheckBoxSongCard):
        """ 将歌曲卡信号连接到槽 """
        songCard.doubleClicked.connect(self.playSignal)
        songCard.playButtonClicked.connect(self.__onPlayButtonClicked)
        songCard.clicked.connect(self.setCurrentIndex)


class OnlineSongListWidget(NoScrollSongListWidget):
    """ 在线音乐歌曲卡列表 """

    playSignal = pyqtSignal(int)                 # 将播放列表的当前歌曲切换为指定的歌曲卡
    downloadSig = pyqtSignal(SongInfo, str)      # 下载歌曲 (songInfo, quality)

    def __init__(self, parent=None):
        """
        Parameters
        ----------
        parent:
            父级窗口
        """
        super().__init__(None, SongCardType.ONLINE_SONG_CARD,
                         parent, QMargins(30, 0, 30, 0), 0)
        self.__setQss()

    def __onPlayButtonClicked(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(index)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            menu = OnlineSongListContextMenu(self)
            self.__connectContextMenuSignalToSlot(menu)
            menu.exec(self.cursor().pos())

    def __setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/song_tab_interface_song_list_widget.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def _connectSongCardSignalToSlot(self, songCard: OnlineSongCard):
        """ 将歌曲卡信号连接到槽 """
        songCard.doubleClicked.connect(self.playSignal)
        songCard.playButtonClicked.connect(self.__onPlayButtonClicked)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.downloadSig.connect(self.downloadSig)

    def __connectContextMenuSignalToSlot(self, menu):
        """ 将右击菜单信号连接到槽函数 """
        menu.showPropertyAct.triggered.connect(
            self.showSongPropertyDialog)
        menu.playAct.triggered.connect(
            lambda: signalBus.playOneSongCardSig.emit(self.currentSongInfo))
        menu.nextSongAct.triggered.connect(
            lambda: signalBus.nextToPlaySig.emit([self.currentSongInfo]))
        menu.downloadMenu.downloadSig.connect(
            lambda quality: self.downloadSig.emit(self.currentSongInfo, quality))


class LocalSongListContextMenu(DWMMenu):
    """ 本地音乐歌曲卡列表右击菜单 """

    def __init__(self, parent):
        super().__init__("", parent)
        # 创建主菜单动作
        self.playAct = QAction(self.tr("Play"), self)
        self.nextSongAct = QAction(self.tr("Play next"), self)
        self.showAlbumAct = QAction(self.tr("Show album"), self)
        self.showPropertyAct = QAction(self.tr("Properties"), self)
        # 创建菜单和子菜单
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        # 将动作添加到菜单中
        self.addActions([self.playAct, self.nextSongAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        # 将其余动作添加到主菜单
        self.addActions(
            [self.showAlbumAct, self.showPropertyAct])


class OnlineSongListContextMenu(DWMMenu):
    """ 在线音乐歌曲卡列表右击菜单 """

    def __init__(self, parent):
        super().__init__("", parent)
        self.setObjectName('onlineSongListContextMenu')
        # 创建主菜单动作
        self.playAct = QAction(self.tr("Play"), self)
        self.nextSongAct = QAction(self.tr("Play next"), self)
        self.showPropertyAct = QAction(self.tr("Properties"), self)
        # 创建菜单和子菜单
        self.downloadMenu = DownloadMenu(self.tr('Download'), self)
        # 将动作添加到菜单中
        self.addActions([self.playAct, self.nextSongAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.downloadMenu)
        # 将其余动作添加到主菜单
        self.addAction(self.showPropertyAct)
