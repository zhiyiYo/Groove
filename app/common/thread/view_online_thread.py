# coding:utf-8
from enum import Enum

from PyQt5.QtCore import QThread, pyqtSignal

from common.database.entity import SongInfo, AlbumInfo, SingerInfo
from common.crawler import KuWoMusicCrawler, WanYiMusicCrawler, QueryServerType


class ViewOnlineType(Enum):
    """ View online type """
    SONG = 0
    ALBUM = 1
    SINGER = 2


class ViewOnlineThread(QThread):
    """ View online thread """

    crawlFinished = pyqtSignal(ViewOnlineType, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.keyWord = ''
        self.task = None
        self.onlineType = ViewOnlineType.SONG
        self.kuwoCrawler = KuWoMusicCrawler()
        self.wanyiCrawler = WanYiMusicCrawler()

    def run(self):
        url = self.task(self.keyWord)
        self.crawlFinished.emit(self.onlineType, url)

    def getSongDetailsUrl(self, songInfo: SongInfo, server=QueryServerType.KUWO):
        """ get song details url

        Paramters
        ---------
        songInfo: SongInfo
            song information

        server: QueryServerType
            the server to crawl
        """
        singer = songInfo.singer or ''
        songName = songInfo.title or ''
        self.keyWord = singer + ' ' + songName
        self.onlineType = ViewOnlineType.SONG

        # select the server to crawl
        if server == QueryServerType.KUWO:
            self.task = self.kuwoCrawler.getSongDetailsUrl
        else:
            self.task = self.wanyiCrawler.getSongDetailsUrl

        self.start()

    def getAlbumDetailsUrl(self, albumInfo: AlbumInfo):
        """ get album details url

        Parameters
        ----------
        albumInfo: AlbumInfo
            album information
        """
        singer = albumInfo.singer or ''
        album = albumInfo.album or ''
        self.keyWord = singer + ' ' + album
        self.onlineType = ViewOnlineType.ALBUM
        self.task = self.wanyiCrawler.getAlbumDetailsUrl
        self.start()

    def getSingerDetailsUrl(self, singerInfo: SingerInfo):
        """ get singer details url

        Parameters
        ----------
        singerInfo: SingerInfo
            singer information
        """
        self.keyWord = singerInfo.singer or ''
        self.onlineType = ViewOnlineType.SINGER
        self.task = self.wanyiCrawler.getSingerDetailsUrl
        self.start()
