# coding:utf-8
import os

from app.common.crawler.kuwo_music_crawler import KuWoMusicCrawler
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class GetSingerAvatarThread(QThread):
    """ 获取歌手头像线程 """

    downloadFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.singer = ''
        self.saveDir = 'app/resource/singer_avatar'
        self.crawler = KuWoMusicCrawler()

    def run(self):
        """ 获取头像 """
        self.crawler.getSingerAvatar(self.singer, self.saveDir)
        self.downloadFinished.emit(f'{self.saveDir}/{self.singer}.jpg')
