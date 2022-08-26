# coding:utf-8
from typing import List

from common.config import config
from common.crawler import (CrawlerBase, KuGouMusicCrawler, KuWoMusicCrawler,
                            WanYiMusicCrawler, QQMusicCrawler)
from PyQt5.QtCore import QThread, pyqtSignal


class GetMvUrlThread(QThread):
    """ Thread used to get the play url of MV """

    crawlFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.key_word = ''
        self.crawlers = [
            KuGouMusicCrawler(),
            WanYiMusicCrawler(),
            QQMusicCrawler(),
            KuWoMusicCrawler()
        ]   #type:List[CrawlerBase]

    def run(self):
        url = ''
        for crawler in self.crawlers:
            mvInfo = crawler.getMvInfo(self.key_word)
            if not mvInfo:
                continue

            url = crawler.getMvUrl(mvInfo, config.get(config.onlineMvQuality))
            if url:
                break

        self.crawlFinished.emit(url)

    def search(self, singer: str, title: str):
        """ search mv url

        Parameters
        ----------
        singer: str
            singer name

        title: str
            song name
        """
        self.key_word = singer + ' ' + title
        self.start()