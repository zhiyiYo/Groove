# coding:utf-8
import os
from pathlib import Path
from typing import Dict, List

from common.crawler import KuWoMusicCrawler
from common.database.entity import AlbumInfo, SingerInfo
from common.library import Library
from common.thread.get_singer_avatar_thread import GetSingerAvatarThread
from components.album_card import (AlbumBlurBackground, AlbumCardType,
                                   GridAlbumCardView, SingerInterfaceAlbumCard)
from components.buttons.three_state_button import ThreeStateButton
from components.dialog_box.message_dialog import MessageDialog
from components.layout.grid_layout import GridLayout
from components.widgets.menu import AddToMenu
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import (QFile, QMargins, QParallelAnimationGroup, QPoint, Qt,
                          pyqtSignal)
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

from .selection_mode_bar import SelectionModeBar
from .singer_info_bar import SingerInfoBar


class SingerInterface(ScrollArea):
    """ 歌手界面 """

    playSig = pyqtSignal(list)                                  # 播放信号
    nextToPlaySig = pyqtSignal(list)                            # 下一首播放
    removeSongSig = pyqtSignal(list)                            # 删除歌曲
    selectionModeStateChanged = pyqtSignal(bool)                # 进入/退出选择模式
    switchToAlbumInterfaceSig = pyqtSignal(str, str)            # 切换到专辑界面
    editAlbumInfoSignal = pyqtSignal(AlbumInfo, AlbumInfo, str)  # 编辑专辑信息
    addSongsToPlayingPlaylistSig = pyqtSignal(list)             # 将歌曲添加到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)           # 将专辑添加到新建的播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)         # 专辑添加到已存在的播放列表

    def __init__(self, library: Library, singerInfo: SingerInfo = None, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        singerInfo: SingerInfo
            歌手信息

        parent:
            父级
        """
        super().__init__(parent=parent)
        self.library = library
        self.columnNum = 5
        self.isInSelectionMode = False
        self.isAllAlbumCardsChecked = False
        self.checkedAlbumCards = []     # type:List[SingerInterfaceAlbumCard]
        self.crawler = KuWoMusicCrawler()
        self.getAvatarThread = GetSingerAvatarThread(self)

        # 创建小部件
        self.__getInfo(singerInfo)
        self.scrollWidget = QWidget(self)
        self.singerInfoBar = SingerInfoBar(self.singerInfo, self)
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.albumBlurBackground = AlbumBlurBackground(self.scrollWidget)
        self.albumCardView = GridAlbumCardView(
            self.library,
            self.albumInfos,
            AlbumCardType.SINGER_INTERFACE_ALBUM_CARD,
            spacings=(10, 10),
            margins=QMargins(30, 456, 30, 0),
            parent=self.scrollWidget
        )
        self.inYourMusicLabel = QLabel(
            self.tr('In your music'), self.scrollWidget)
        self.playButton = ThreeStateButton(
            {
                "normal": ":/images/singer_interface/Play_normal.png",
                "hover": ":/images/singer_interface/Play_hover.png",
                "pressed": ":/images/singer_interface/Play_pressed.png",
            },
            self.scrollWidget,
            (20, 20)
        )
        self.selectionModeBar = SelectionModeBar(self)
        self.albumCards = self.albumCardView.albumCards

        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.__setQss()
        self.setWidget(self.scrollWidget)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.inYourMusicLabel.move(30, 412)
        self.playButton.move(185, 419)
        self.selectionModeBar.hide()
        self.__connectSignalToSlot()
        self.resize(1270, 900)

    def __getAlbumSongInfos(self, singer: str, album: str):
        """ 获取一张专辑歌曲信息列表 """
        albumInfo = self.library.albumInfoController.getAlbumInfo(
            singer, album)

        if not albumInfo:
            return []

        return albumInfo.songInfos

    def __getAlbumsSongInfos(self, albums: List[str]):
        """ 获取多张专辑歌曲信息列表 """
        if not albums:
            return []

        singers = [self.singer]*len(albums)
        songInfos = self.library.songInfoController.getSongInfosBySingerAlbum(
            singers, albums)

        return songInfos

    def __getCheckedAlbumCardSongInfos(self):
        """ 获取选中的专辑卡的歌曲信息 """
        singers = [self.singer]*len(self.checkedAlbumCards)
        albums = [i.album for i in self.checkedAlbumCards]
        return self.library.songInfoController.getSongInfosBySingerAlbum(singers, albums)

    def getAllSongInfos(self):
        """ 获取所有歌曲信息 """
        albums = [i.album for i in self.albumInfos]
        return self.__getAlbumsSongInfos(albums)

    def resizeEvent(self, e):
        self.singerInfoBar.resize(self.width(), self.singerInfoBar.height())
        self.albumCardView.setFixedWidth(self.width())
        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())
        self.scrollWidget.resize(
            self.width(), 456 + self.albumCardView.gridLayout.rowCount()*300 + 120)

    def __getInfo(self, singerInfo: SingerInfo):
        """ 获取信息 """
        self.singerInfo = singerInfo or SingerInfo()
        self.singer = self.singerInfo.singer or ''
        self.genre = self.singerInfo.genre or ''
        self.albumInfos = self.library.albumInfoController.getAlbumInfosBySinger(
            self.singer)

    def __setQss(self):
        """ 设置层叠样式 """
        self.scrollWidget.setObjectName('scrollWidget')
        self.inYourMusicLabel.setObjectName('inYourMusicLabel')

        f = QFile(":/qss/singer_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.inYourMusicLabel.adjustSize()

    def __onSelectionModeBarDeleteButtonClicked(self):
        """ 选择模式栏删除按钮点击槽函数 """
        if len(self.checkedAlbumCards) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these albums, they won't be on be this device anymore.")
        else:
            name = self.checkedAlbumCards[0].album
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(self.__onDeleteAlbumsYesButtonClicked)
        w.exec()

    def __onDeleteAlbumsYesButtonClicked(self):
        """ 专辑界面选择模式栏删除按钮点击槽函数 """
        songInfos = self.__getCheckedAlbumCardSongInfos()
        self.__unCheckAlbumCards()
        songPaths = [i.file for i in songInfos]
        self.removeSongSig.emit(songPaths)

    # TODO:删除专辑
    def deleteAlbums(self, albumNames: list):
        """ 删除专辑 """

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ 显示磨砂背景 """
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.albumBlurBackground.show()

    def __onAlbumCardCheckedStateChanged(self, albumCard, isChecked: bool):
        """ 专辑卡选中状态改变对应的槽函数 """
        # 如果专辑信息不在选中的专辑信息列表中且对应的专辑卡变为选中状态就将专辑信息添加到列表中
        if albumCard not in self.checkedAlbumCards and isChecked:
            self.checkedAlbumCards.append(albumCard)

        # 如果专辑信息已经在列表中且该专辑卡变为非选中状态就弹出该专辑信息
        elif albumCard in self.checkedAlbumCards and not isChecked:
            self.checkedAlbumCards.pop(
                self.checkedAlbumCards.index(albumCard))

        self.selectionModeBar.setPartButtonHidden(
            len(self.checkedAlbumCards) > 1)
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())

        # 检查是否全部专辑卡选中改变
        isAllChecked = len(self.checkedAlbumCards) == len(self.albumCards)
        if isAllChecked != self.isAllAlbumCardsChecked:
            self.isAllAlbumCardsChecked = isAllChecked
            self.selectionModeBar.checkAllButton.setCheckedState(
                not isAllChecked)

        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            self.__setAllAlbumCardSelectionModeOpen(True)
            self.selectionModeStateChanged.emit(True)
            self.isInSelectionMode = True
        elif not self.checkedAlbumCards:
            self.__setAllAlbumCardSelectionModeOpen(False)
            self.selectionModeStateChanged.emit(False)
            self.isInSelectionMode = False

    def __setAllAlbumCardSelectionModeOpen(self, isOpen: bool):
        """ 设置所有专辑卡是否进入选择模式 """
        self.selectionModeBar.setVisible(isOpen)
        for albumCard in self.albumCards:
            albumCard.setSelectionModeOpen(isOpen)

        # 退出选择模式时开启隐藏所有复选框的动画
        if not isOpen:
            self.albumCardView.hideCheckBoxAniGroup.start()

    def __onScrollBarValueChanged(self, value):
        """ 滚动时改变专辑信息栏高度 """
        h = 385 - value
        if h > 155:
            self.singerInfoBar.resize(self.width(), h)

    def __getSingerAvatar(self, singer: str):
        """ 获取歌手头像 """
        avatars = [i.stem for i in Path('cache/singer_avatar').glob('*')]
        if singer not in avatars:
            self.singerInfoBar.coverLabel.hide()
            self.getAvatarThread.singer = singer
            self.getAvatarThread.start()

    def __onDownloadAvatarFinished(self, avatarPath: str):
        """ 下载歌手头像完成 """
        self.singerInfoBar.coverLabel.show()
        if os.path.exists(avatarPath):
            self.singerInfoBar.updateCover(avatarPath)

    def updateWindow(self, singerInfo: SingerInfo):
        """ 更新窗口 """
        if self.singerInfo == singerInfo:
            return

        self.__getInfo(singerInfo)
        self.__getSingerAvatar(self.singerInfo.singer)
        self.albumCardView.updateAllAlbumCards(self.albumInfos)
        self.singerInfoBar.updateWindow(self.singerInfo)
        self.scrollWidget.resize(
            self.width(), 456 + self.albumCardView.gridLayout.rowCount()*300 + 120)

    def showEvent(self, e):
        self.albumBlurBackground.hide()
        super().showEvent(e)

    def __onSelectionModeBarPlayButtonClicked(self):
        """ 选择模式栏播放/下一首播放按钮槽函数 """
        songInfos = self.__getCheckedAlbumCardSongInfos()
        self.__unCheckAlbumCards()

        if self.sender() is self.selectionModeBar.playButton:
            self.playSig.emit(songInfos)
        elif self.sender() is self.selectionModeBar.nextToPlayButton:
            self.nextToPlaySig.emit(songInfos)

    def __unCheckAlbumCards(self):
        """ 取消选中所有专辑卡 """
        self.selectionModeBar.checkAllButton.setCheckedState(True)
        checkedCards = self.checkedAlbumCards.copy()
        for albumCard in checkedCards:
            albumCard.setChecked(False)

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        addToButton = self.sender()

        # 获取选中的播放列表
        songInfos = self.__getCheckedAlbumCardSongInfos()

        # 计算菜单弹出位置
        pos = self.selectionModeBar.mapToGlobal(addToButton.pos())
        x = pos.x() + addToButton.width() + 5
        y = pos.y() + int(
            addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)

        # 信号连接到槽
        for act in menu.action_list:
            act.triggered.connect(self.exitSelectionMode)
        menu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(songInfos))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfos))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfos))
        menu.exec(QPoint(x, y))

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__unCheckAlbumCards()

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 播放全部按钮槽函数
        self.playButton.clicked.connect(
            lambda: self.playSig.emit(self.getAllSongInfos()))

        # 将滚动信号连接到槽函数
        self.verticalScrollBar().valueChanged.connect(self.__onScrollBarValueChanged)

        # 将歌手信息栏信号连接到槽函数
        self.singerInfoBar.playAllButton.clicked.connect(
            lambda: self.playSig.emit(self.getAllSongInfos()))
        self.singerInfoBar.addSongsToPlayingPlaylistSig.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(self.getAllSongInfos()))
        self.singerInfoBar.addSongsToNewCustomPlaylistSig.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(self.getAllSongInfos()))
        self.singerInfoBar.addSongsToCustomPlaylistSig.connect(
            lambda n: self.addSongsToCustomPlaylistSig.emit(n, self.getAllSongInfos()))

        # 将选择模式栏信号连接到槽函数
        self.selectionModeBar.playButton.clicked.connect(
            self.__onSelectionModeBarPlayButtonClicked)
        self.selectionModeBar.nextToPlayButton.clicked.connect(
            self.__onSelectionModeBarPlayButtonClicked)
        self.selectionModeBar.deleteButton.clicked.connect(
            self.__onSelectionModeBarDeleteButtonClicked)
        self.selectionModeBar.addToButton.clicked.connect(self.__showAddToMenu)

        # 将歌手头像下载线程信号连接到槽
        self.getAvatarThread.downloadFinished.connect(
            self.__onDownloadAvatarFinished)

        # 将专辑卡视图信号连接到槽函数
        self.albumCardView.playSig.connect(
            lambda s, a: self.playSig.emit(self.__getAlbumSongInfos(s, a)))
        self.albumCardView.nextPlaySig.connect(self.nextToPlaySig)
        self.albumCardView.deleteAlbumSig.connect(
            lambda s, a: self.removeSongSig.emit(self.__getAlbumSongInfos(s, a)))
        self.albumCardView.addAlbumToPlayingSig.connect(
            self.addSongsToPlayingPlaylistSig)
        self.albumCardView.addAlbumToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        self.albumCardView.addAlbumToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.albumCardView.checkedStateChanged.connect(
            self.__onAlbumCardCheckedStateChanged)
        self.albumCardView.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        self.albumCardView.showBlurAlbumBackgroundSig.connect(
            self.__showBlurAlbumBackground)
        self.albumCardView.hideBlurAlbumBackgroundSig.connect(
            self.albumBlurBackground.hide)
