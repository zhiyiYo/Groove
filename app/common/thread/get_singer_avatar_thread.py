# coding:utf-8
from typing import List

from common.crawler import KuWoMusicCrawler, WanYiMusicCrawler, CrawlerBase
from PyQt5.QtCore import pyqtSignal, QThread


class GetSingerAvatarThread(QThread):
    """ Thread used to get singer avatar """

    downloadFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.singer = ''
        self.crawlers = [
            WanYiMusicCrawler(),
            KuWoMusicCrawler()
        ]   # type:List[CrawlerBase]

    def run(self):
        """ start to get avatar """
        for crawler in self.crawlers:
            save_path = crawler.getSingerAvatar(self.singer)
            if save_path:
                break

        self.downloadFinished.emit(save_path)

    def get(self, singer: str):
        """ get singer avatar

        Parameters
        ----------
        singer: str
            歌手名
        """
        self.singer = singer
        self.start()
