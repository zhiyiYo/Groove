# coding:utf-8
from common.database.entity import AlbumInfo
from common.crawler import WanYiMusicCrawler
from PyQt5.QtCore import QThread, pyqtSignal


class GetAlbumDetailsUrlThread(QThread):
    """ get album details url thread """

    crawlFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.albumInfo = AlbumInfo()
        self.crawler = WanYiMusicCrawler()

    def run(self):
        singer = self.albumInfo.singer or ''
        album = self.albumInfo.album or ''
        keyWord = singer + ' ' + album

        url = self.crawler.getAlbumDetailsUrl(keyWord)
        self.crawlFinished.emit(url)

    def get(self, albumInfo: AlbumInfo):
        """ get song details url

        Paramters
        ---------
        albumInfo: AlbumInfo
            album information
        """
        self.albumInfo = albumInfo
        self.start()
