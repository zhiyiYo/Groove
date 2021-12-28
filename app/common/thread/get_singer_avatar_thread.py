# coding:utf-8
from common.crawler.kuwo_music_crawler import KuWoMusicCrawler
from PyQt5.QtCore import pyqtSignal, QThread


class GetSingerAvatarThread(QThread):
    """ 获取歌手头像线程 """

    downloadFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.singer = ''
        self.saveDir = 'cache/singer_avatar'
        self.crawler = KuWoMusicCrawler()

    def run(self):
        """ 获取头像 """
        self.crawler.getSingerAvatar(self.singer, self.saveDir)
        self.downloadFinished.emit(f'{self.saveDir}/{self.singer}.jpg')
