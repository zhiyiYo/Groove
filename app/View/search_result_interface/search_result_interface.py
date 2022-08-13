# coding:utf-8
from math import ceil

from common.config import config
from common.icon import getIconColor
from common.crawler import KuWoMusicCrawler
from common.database.entity import SongInfo
from common.library import Library
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from common.thread.download_song_thread import DownloadSongThread
from components.widgets.label import PixmapLabel
from components.widgets.scroll_area import ScrollArea
from components.widgets.tooltip import DownloadStateTooltip
from PyQt5.QtCore import QFile, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from .album_group_box import AlbumGroupBox
from .playlist_group_box import PlaylistGroupBox
from .singer_group_box import SingerGroupBox
from .song_group_box import SongGroupBox


class SearchResultInterface(ScrollArea):
    """ Search result interface """

    playLocalSongSig = pyqtSignal(int)    # 播放本地歌曲
    playOnlineSongSig = pyqtSignal(int)   # 播放在线音乐

    def __init__(self, library: Library, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        parent:
            parent window
        """
        super().__init__(parent=parent)
        self.library = library
        self.keyWord = ''            # searched key word
        self.playlists = {}          # matched local playlists
        self.albumInfos = []         # matched album information
        self.singerInfos = []        # matched singer information
        self.localSongInfos = []     # matched song information
        self.onlineSongInfos = []    # matched online information

        self.titleLabel = QLabel(self)
        self.searchLabel = PixmapLabel(self)
        self.scrollWidget = QWidget(self)
        self.vBox = QVBoxLayout(self.scrollWidget)
        self.albumGroupBox = AlbumGroupBox(library, self.scrollWidget)
        self.singerGroupBox = SingerGroupBox(library, self.scrollWidget)
        self.playlistGroupBox = PlaylistGroupBox(library, self.scrollWidget)
        self.localSongGroupBox = SongGroupBox('Local songs', self.scrollWidget)
        self.onlineSongGroupBox = SongGroupBox(
            'Online songs', self.scrollWidget)
        self.searchOthersLabel = QLabel(
            self.tr("Try searching for something else."), self)
        self.checkSpellLabel = QLabel(
            self.tr('Check your spelling, or search for something else'), self)

        self.localSongListWidget = self.localSongGroupBox.songListWidget
        self.onlineSongListWidget = self.onlineSongGroupBox.songListWidget

        self.crawler = KuWoMusicCrawler()
        self.totalPages = 1                             # 在线音乐总分页数
        self.currentPage = 1                            # 当前在线音乐页码
        self.totalOnlineMusic = 0                       # 数据库中所有符合条件的在线音乐数

        self.downloadSongThread = DownloadSongThread(self)
        self.downloadStateTooltip = None
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.vBox.setSpacing(20)
        self.vBox.setContentsMargins(0, 10, 0, 116)
        self.vBox.addWidget(self.singerGroupBox)
        self.vBox.addWidget(self.albumGroupBox)
        self.vBox.addWidget(self.playlistGroupBox)
        self.vBox.addWidget(self.localSongGroupBox)
        self.vBox.addWidget(self.onlineSongGroupBox)
        self.setWidget(self.scrollWidget)
        self.setViewportMargins(0, 115, 0, 0)
        self.__setQss()
        self.searchLabel.setPixmap(
            QPixmap(f":/images/search_result_interface/Search_{getIconColor()}.png"))
        self.__setHintsLabelVisible(False)
        self.titleLabel.move(30, 55)
        self.titleLabel.raise_()
        self.resize(1200, 500)
        self.__connectSignalToSlot()

    def resizeEvent(self, e):
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())
        self.singerGroupBox.resize(self.width(), self.singerGroupBox.height())
        self.albumGroupBox.resize(self.width(), self.albumGroupBox.height())
        self.localSongGroupBox.resize(
            self.width(), self.localSongGroupBox.height())
        self.onlineSongGroupBox.resize(
            self.width(), self.onlineSongGroupBox.height())
        self.searchLabel.move(self.width()//2-self.searchLabel.width()//2, 138)
        self.checkSpellLabel.move(
            self.width()//2-self.checkSpellLabel.width()//2, 225)
        self.searchOthersLabel.move(
            self.width()//2-self.searchOthersLabel.width()//2, 300)
        self.playlistGroupBox.resize(
            self.width(), self.playlistGroupBox.height())

    def __setQss(self):
        """ set style sheet """
        self.titleLabel.setObjectName('titleLabel')
        self.checkSpellLabel.setObjectName('checkSpellLabel')
        self.searchOthersLabel.setObjectName('searchOthersLabel')
        setStyleSheet(self, 'search_result_interface')
        self.checkSpellLabel.adjustSize()
        self.searchOthersLabel.adjustSize()

    def __setHintsLabelVisible(self, isVisible: bool):
        """ set the visibility of hints label """
        self.searchLabel.setVisible(isVisible)
        self.checkSpellLabel.setVisible(isVisible)
        self.searchOthersLabel.setVisible(isVisible)

    def __downloadSong(self, songInfo: SongInfo, quality: str):
        """ download online music """
        self.downloadSongThread.appendDownloadTask(songInfo, quality)
        if self.downloadSongThread.isRunning():
            self.downloadStateTooltip.appendOneDownloadTask()
            return

        title = self.tr('Downloading songs')
        content = self.tr('There are') + f' {1} ' + \
            self.tr('left. Please wait patiently')
        self.downloadStateTooltip = DownloadStateTooltip(
            title, content, 1, self.window())
        self.downloadSongThread.downloadOneSongFinished.connect(
            self.downloadStateTooltip.completeOneDownloadTask)

        self.downloadStateTooltip.show()
        self.downloadSongThread.start()

    def __onDownloadAllComplete(self):
        """ download finished slot """
        self.downloadStateTooltip = None

    def search(self, keyWord: str):
        """ search local songs, albums, playlist and online songs """
        self.keyWord = keyWord

        # match singer information
        self.singerInfos = self.library.singerInfoController.getSingerInfosLike(
            singer=keyWord
        )

        # match album information
        self.albumInfos = self.library.albumInfoController.getAlbumInfosLike(
            singer=keyWord,
            album=keyWord
        )

        # match local song information
        self.localSongInfos = self.library.songInfoController.getSongInfosLike(
            file=keyWord,
            title=keyWord,
            singer=keyWord,
            album=keyWord
        )

        # match local playlist
        self.playlists = self.library.playlistController.getPlaylistsLike(
            name=keyWord,
            singer=keyWord,
            album=keyWord
        )

        # search online songs
        self.currentPage = 1
        self.onlineSongInfos, self.totalOnlineMusic = self.crawler.getSongInfos(
            keyWord, 1, config['online-music-page-size'])
        self.totalPages = 1 if not self.totalOnlineMusic else ceil(
            self.totalOnlineMusic/config['online-music-page-size'])

        self.__updateLoadMoreLabel()

        # update window
        self.titleLabel.setText(f'"{keyWord}"'+self.tr('Search Result'))
        self.titleLabel.adjustSize()
        self.singerGroupBox.updateWindow(self.singerInfos)
        self.albumGroupBox.updateWindow(self.albumInfos)
        self.playlistGroupBox.updateWindow(self.playlists)
        self.localSongGroupBox.updateWindow(self.localSongInfos[:5])
        self.onlineSongGroupBox.updateWindow(self.onlineSongInfos)

        self.__adjustHeight()
        self.__updateWidgetsVisible()
        self.verticalScrollBar().setValue(0)

    def __adjustHeight(self):
        """ adjust window height """
        isSingerVisible = len(self.singerInfos) > 0
        isAlbumVisible = len(self.albumInfos) > 0
        isPlaylistVisible = len(self.playlists) > 0
        isLocalSongVisible = len(self.localSongInfos) > 0
        isOnlineSongVisible = len(self.onlineSongInfos) > 0

        visibleNum = isAlbumVisible+isLocalSongVisible + \
            isPlaylistVisible+isOnlineSongVisible+isSingerVisible
        spacing = 0 if not visibleNum else (visibleNum-1)*20

        self.scrollWidget.resize(
            self.width(),
            241 +
            isSingerVisible*self.singerGroupBox.height() +
            isAlbumVisible*self.albumGroupBox.height() +
            isLocalSongVisible*self.localSongGroupBox.height() +
            isOnlineSongVisible*self.onlineSongGroupBox.height() +
            isPlaylistVisible*self.playlistGroupBox.height() + spacing
        )
        self.__setHintsLabelVisible(visibleNum == 0)

    def __updateWidgetsVisible(self):
        """ update the visibility of widgets """
        self.singerGroupBox.setVisible(bool(self.singerInfos))
        self.albumGroupBox.setVisible(bool(self.albumInfos))
        self.playlistGroupBox.setVisible(bool(self.playlists))
        self.localSongGroupBox.setVisible(bool(self.localSongInfos))
        self.onlineSongGroupBox.setVisible(bool(self.onlineSongInfos))
        if self.albumGroupBox.isHidden() and self.localSongGroupBox.isHidden() and \
                self.playlistGroupBox.isHidden() and self.onlineSongGroupBox.isHidden():
            self.__setHintsLabelVisible(True)

    def __updateLoadMoreLabel(self):
        """ update load more label """
        label = self.onlineSongGroupBox.loadMoreLabel

        if self.currentPage < self.totalPages:
            label.setText(self.tr('Load more'))
            label.setProperty('loadFinished', 'false')
            label.setCursor(Qt.PointingHandCursor)
        else:
            label.setText(self.tr('No more results'))
            label.setProperty('loadFinished', 'true')
            label.setCursor(Qt.ArrowCursor)

        label.adjustSize()
        label.setStyle(QApplication.style())

    def __loadMoreOnlineMusic(self):
        """ load more online music """
        if self.currentPage == self.totalPages:
            return

        # send request for online music
        self.currentPage += 1
        songInfos, _ = self.crawler.getSongInfos(
            self.keyWord, self.currentPage, config['online-music-page-size'])

        # update online music group box
        offset = len(self.onlineSongListWidget.songInfos)
        self.onlineSongGroupBox.loadMoreOnlineMusic(songInfos)
        self.onlineSongInfos = self.onlineSongListWidget.songInfos

        self.__updateLoadMoreLabel()
        self.__adjustHeight()

    def deletePlaylistCard(self, name: str):
        """ delete a playlist card """
        self.playlistGroupBox.playlistCardView.deletePlaylistCard(name)
        if len(self.playlistGroupBox.playlistCards) == 0:
            self.playlistGroupBox.hide()
            self.__adjustHeight()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        # local song group box signal
        self.localSongGroupBox.switchToMoreSearchResultInterfaceSig.connect(
            lambda: signalBus.switchToMoreSearchResultInterfaceSig.emit(self.keyWord, 'local song', self.localSongInfos))
        self.localSongListWidget.playSignal.connect(self.playLocalSongSig)
        self.localSongListWidget.currentIndexChanged.connect(
            self.onlineSongListWidget.cancelSelectedState)

        # online song group box signal
        self.onlineSongListWidget.playSignal.connect(self.playOnlineSongSig)
        self.onlineSongListWidget.downloadSig.connect(self.__downloadSong)
        self.onlineSongGroupBox.loadMoreSignal.connect(
            self.__loadMoreOnlineMusic)
        self.onlineSongListWidget.currentIndexChanged.connect(
            self.localSongListWidget.cancelSelectedState)

        # album group box signal
        self.singerGroupBox.switchToMoreSearchResultInterfaceSig.connect(
            lambda: signalBus.switchToMoreSearchResultInterfaceSig.emit(self.keyWord, 'singer', self.singerInfos))

        # album group box signal
        self.albumGroupBox.switchToMoreSearchResultInterfaceSig.connect(
            lambda: signalBus.switchToMoreSearchResultInterfaceSig.emit(self.keyWord, 'album', self.albumInfos))

        # playlist group box signal
        self.playlistGroupBox.switchToMoreSearchResultInterfaceSig.connect(
            lambda: signalBus.switchToMoreSearchResultInterfaceSig.emit(self.keyWord, 'playlist', self.playlists))

        # down thread signal
        self.downloadSongThread.finished.connect(self.__onDownloadAllComplete)
