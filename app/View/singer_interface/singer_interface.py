# coding:utf-8
import os
from pathlib import Path

from common.cache import singerAvatarFolder
from common.icon import getIconColor
from common.crawler import KuWoMusicCrawler
from common.database.entity import SingerInfo
from common.library import Library
from common.os_utils import adjustName
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from common.thread.get_singer_avatar_thread import GetSingerAvatarThread
from components.album_card import (AlbumBlurBackground, AlbumCardType,
                                   GridAlbumCardView)
from components.buttons.three_state_button import ThreeStateButton
from components.selection_mode_interface import (AlbumSelectionModeInterface,
                                                 SelectionModeBarType)
from PyQt5.QtCore import QMargins, QPoint
from PyQt5.QtWidgets import QLabel

from .singer_info_bar import SingerInfoBar


class SingerInterface(AlbumSelectionModeInterface):
    """ Singer interface """

    def __init__(self, library: Library, singerInfo: SingerInfo = None, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        singerInfo: SingerInfo
            singer information

        parent:
            parent window
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

        self.singerInfoBar = SingerInfoBar(self.singerInfo, self)
        self.albumBlurBackground = AlbumBlurBackground(self.scrollWidget)
        self.inYourMusicLabel = QLabel(
            self.tr('In your music'), self.scrollWidget)
        c = getIconColor()
        self.playButton = ThreeStateButton(
            {
                "normal": f":/images/singer_interface/Play_{c}_normal.png",
                "hover": f":/images/singer_interface/Play_{c}_hover.png",
                "pressed": f":/images/singer_interface/Play_{c}_pressed.png",
            },
            self.scrollWidget,
            (20, 20)
        )
        self.albumCards = self.albumCardView.albumCards

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.__setQss()
        self.vBox.setContentsMargins(0, 456, 0, 120)
        self.inYourMusicLabel.move(30, 412)
        f = self.inYourMusicLabel.fontMetrics()
        self.playButton.move(f.width(self.inYourMusicLabel.text()) + 80, 416)
        self.albumBlurBackground.lower()

        self.__connectSignalToSlot()
        self.resize(1270, 900)

    def getAllSongInfos(self):
        """ get all song information of singer """
        albums = [i.album for i in self.albumInfos]
        singers = [self.singer]*len(albums)
        songInfos = self.library.songInfoController.getSongInfosBySingerAlbum(
            singers, albums)
        return songInfos

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.singerInfoBar.resize(self.width(), self.singerInfoBar.height())

    def __getInfo(self, singerInfo: SingerInfo):
        """ get singer information """
        self.singerInfo = singerInfo or SingerInfo()
        self.singer = self.singerInfo.singer or ''
        self.genre = self.singerInfo.genre or ''
        self.albumInfos = self.library.albumInfoController.getAlbumInfosBySinger(
            self.singer)

    def __setQss(self):
        """ set style sheet """
        self.inYourMusicLabel.setMinimumSize(140, 25)
        self.inYourMusicLabel.setObjectName('inYourMusicLabel')
        setStyleSheet(self, 'singer_interface')
        self.inYourMusicLabel.adjustSize()

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ show blurred album background """
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.albumBlurBackground.show()

    def __onScrollBarValueChanged(self, value):
        """ adjust the height of singer information bar when scrolling """
        h = 385 - value
        if h > 155:
            self.singerInfoBar.resize(self.width(), h)

    def __getSingerAvatar(self, singer: str):
        """ get singer avatar """
        folders = [i.stem for i in singerAvatarFolder.glob('*') if i.is_dir()]
        if adjustName(singer) not in folders:
            self.singerInfoBar.coverLabel.hide()
            self.getAvatarThread.singer = singer
            self.getAvatarThread.start()

    def __onDownloadAvatarFinished(self, avatarPath: str):
        """ download avatar finished """
        self.singerInfoBar.coverLabel.show()
        if os.path.exists(avatarPath):
            self.singerInfoBar.updateCover(avatarPath)

    def updateWindow(self, singerInfo: SingerInfo):
        """ update singer interface """
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
        """ connect signal to slot """
        self.playButton.clicked.connect(
            lambda: signalBus.playCheckedSig.emit(self.getAllSongInfos()))

        self.verticalScrollBar().valueChanged.connect(self.__onScrollBarValueChanged)

        # singer information bar signal
        self.singerInfoBar.playSig.connect(
            lambda: signalBus.playCheckedSig.emit(self.getAllSongInfos()))
        self.singerInfoBar.addToPlayingPlaylistSig.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit(self.getAllSongInfos()))
        self.singerInfoBar.addToNewCustomPlaylistSig.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit(self.getAllSongInfos()))
        self.singerInfoBar.addToCustomPlaylistSig.connect(
            lambda n: signalBus.addSongsToCustomPlaylistSig.emit(n, self.getAllSongInfos()))
        self.singerInfoBar.viewOnlineSig.connect(
            lambda: signalBus.getSingerDetailsUrlSig.emit(self.singerInfo))

        # download avatar thread signal
        self.getAvatarThread.downloadFinished.connect(
            self.__onDownloadAvatarFinished)

        # album card view signal
        self.albumCardView.showBlurAlbumBackgroundSig.connect(
            self.__showBlurAlbumBackground)
        self.albumCardView.hideBlurAlbumBackgroundSig.connect(
            self.albumBlurBackground.hide)
