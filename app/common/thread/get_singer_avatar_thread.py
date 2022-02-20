# coding:utf-8
from common.crawler import KuWoMusicCrawler, WanYiMusicCrawler
from PyQt5.QtCore import pyqtSignal, QThread


class GetSingerAvatarThread(QThread):
    """ Thread used to get singer avatar """

    downloadFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.singer = ''
        self.saveDir = 'cache/singer_avatar'
        self.crawlers = [
            WanYiMusicCrawler(),
            KuWoMusicCrawler()
        ]

    def run(self):
        """ start to get avatar """
        for crawler in self.crawlers:
            save_path = crawler.getSingerAvatar(self.singer, self.saveDir)
            if save_path:
                break

        self.downloadFinished.emit(save_path)
