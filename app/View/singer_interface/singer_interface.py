# coding:utf-8
import os
from pathlib import Path

from common.crawler import KuWoMusicCrawler
from common.database.entity import SingerInfo
from common.library import Library
from common.signal_bus import signalBus
from common.thread.get_singer_avatar_thread import GetSingerAvatarThread
from components.album_card import (AlbumBlurBackground, AlbumCardType,
                                   GridAlbumCardView)
from components.buttons.three_state_button import ThreeStateButton
from components.selection_mode_interface import (AlbumSelectionModeInterface,
                                                 SelectionModeBarType)
from PyQt5.QtCore import QFile, QMargins, QPoint
from PyQt5.QtWidgets import QLabel

from .singer_info_bar import SingerInfoBar


class SingerInterface(AlbumSelectionModeInterface):
    """ 歌手界面 """

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
        view = GridAlbumCardView(
            library,
            [],
            AlbumCardType.SINGER_INTERFACE_ALBUM_CARD,
            spacings=(10, 10),
            margins=QMargins(24, 0, 30, 0),
        )
        super().__init__(library, view, SelectionModeBarType.SINGER, parent)
        self.__getInfo(singerInfo)

        self.columnNum = 5
        self.crawler = KuWoMusicCrawler()
        self.getAvatarThread = GetSingerAvatarThread(self)

        # 创建小部件
        self.singerInfoBar = SingerInfoBar(self.singerInfo, self)
        self.albumBlurBackground = AlbumBlurBackground(self.scrollWidget)
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
        self.albumCards = self.albumCardView.albumCards

        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.__setQss()
        self.vBox.setContentsMargins(0, 456, 0, 120)
        self.inYourMusicLabel.move(30, 412)
        f = self.inYourMusicLabel.fontMetrics()
        self.playButton.move(f.width(self.inYourMusicLabel.text()) + 80, 416)
        self.albumBlurBackground.lower()

        self.__connectSignalToSlot()
        self.resize(1270, 900)

    def getAllSongInfos(self):
        """ 获取所有歌曲信息 """
        albums = [i.album for i in self.albumInfos]
        singers = [self.singer]*len(albums)
        songInfos = self.library.songInfoController.getSongInfosBySingerAlbum(
            singers, albums)
        return songInfos

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.singerInfoBar.resize(self.width(), self.singerInfoBar.height())

    def __getInfo(self, singerInfo: SingerInfo):
        """ 获取信息 """
        self.singerInfo = singerInfo or SingerInfo()
        self.singer = self.singerInfo.singer or ''
        self.genre = self.singerInfo.genre or ''
        self.albumInfos = self.library.albumInfoController.getAlbumInfosBySinger(
            self.singer)

    def __setQss(self):
        """ 设置层叠样式 """
        self.inYourMusicLabel.setMinimumSize(140, 25)
        self.inYourMusicLabel.setObjectName('inYourMusicLabel')

        f = QFile(":/qss/singer_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.inYourMusicLabel.adjustSize()

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ 显示磨砂背景 """
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.albumBlurBackground.show()

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
        self.adjustScrollHeight()

    def showEvent(self, e):
        self.albumBlurBackground.hide()
        super().showEvent(e)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 播放全部按钮槽函数
        self.playButton.clicked.connect(
            lambda: signalBus.playCheckedSig.emit(self.getAllSongInfos()))

        # 将滚动信号连接到槽函数
        self.verticalScrollBar().valueChanged.connect(self.__onScrollBarValueChanged)

        # 将歌手信息栏信号连接到槽函数
        self.singerInfoBar.playAllButton.clicked.connect(
            lambda: signalBus.playCheckedSig.emit(self.getAllSongInfos()))
        self.singerInfoBar.addSongsToPlayingPlaylistSig.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit(self.getAllSongInfos()))
        self.singerInfoBar.addSongsToNewCustomPlaylistSig.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit(self.getAllSongInfos()))
        self.singerInfoBar.addSongsToCustomPlaylistSig.connect(
            lambda n: signalBus.addSongsToCustomPlaylistSig.emit(n, self.getAllSongInfos()))

        # 将歌手头像下载线程信号连接到槽
        self.getAvatarThread.downloadFinished.connect(
            self.__onDownloadAvatarFinished)

        # 将专辑卡视图信号连接到槽函数
        self.albumCardView.showBlurAlbumBackgroundSig.connect(
            self.__showBlurAlbumBackground)
        self.albumCardView.hideBlurAlbumBackgroundSig.connect(
            self.albumBlurBackground.hide)
