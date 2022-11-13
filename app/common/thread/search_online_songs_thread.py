# coding:utf-8
from math import ceil

from PyQt5.QtCore import QThread, pyqtSignal
from common.config import config
from common.signal_bus import signalBus
from common.crawler import KuWoMusicCrawler


class SearchOnlineSongsThread(QThread):
    """ Search online songs thread """

    searchFinished = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.keyWord = ''
        self.currentPage = 1
        self.totalOnlineSongs = 0
        self.crawler = KuWoMusicCrawler()

        signalBus.totalOnlineSongsChanged.connect(self.setTotalOnlineSongs)

    def run(self):
        pageSize = config.get(config.onlinePageSize)
        if self.currentPage >= ceil(self.totalOnlineSongs/pageSize):
            return

        songInfos, total = self.crawler.getSongInfos(
            self.keyWord, self.currentPage+1, pageSize)
        if not total:
            return

        self.currentPage += 1
        self.searchFinished.emit(songInfos)

    def nextPage(self):
        """ next page """
        self.start()

    def setKeyWord(self, keyWord: str):
        """ set the key word to search """
        self.keyWord = keyWord
        self.currentPage = 1

    def setTotalOnlineSongs(self, total: int):
        """ set the total online songs """
        self.totalOnlineSongs = max(total, 0)
