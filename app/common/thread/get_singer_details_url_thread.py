# coding:utf-8
from common.database.entity import SingerInfo
from common.crawler import WanYiMusicCrawler
from PyQt5.QtCore import QThread, pyqtSignal


class GetSingerDetailsUrlThread(QThread):
    """ get singer details url thread """

    crawlFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.singerInfo = SingerInfo()
        self.crawler = WanYiMusicCrawler()

    def run(self):
        singer = self.singerInfo.singer or ''
        url = self.crawler.getSingerDetailsUrl(singer)
        self.crawlFinished.emit(url)

    def get(self, singerInfo: SingerInfo):
        """ get song details url

        Paramters
        ---------
        singerInfo: SingerInfo
            singer information
        """
        self.singerInfo = singerInfo
        self.start()
