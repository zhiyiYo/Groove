# coding:utf-8
from fuzzywuzzy import fuzz
from common.crawler import KuWoMusicCrawler
from PyQt5.QtCore import pyqtSignal, QThread


class GetMvUrlThread(QThread):
    """ 获取 MV 播放地址线程 """

    crawlFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.key_word = ''
        self.crawler = KuWoMusicCrawler()

    def run(self):
        mvInfo_list, _ = self.crawler.getMvInfoList(self.key_word, page_size=1)
        if not mvInfo_list or fuzz.token_set_ratio(mvInfo_list[0]['singer']+' '+mvInfo_list[0]['name'], self.key_word) < 90:
            self.crawlFinished.emit('')
            return

        url = self.crawler.getMvUrl(mvInfo_list[0])
        self.crawlFinished.emit(url)
