# coding:utf-8
import requests
import os

from common.meta_data import AlbumCoverReader
from common.crawler import KuWoMusicCrawler
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class GetOnlineSongUrlThread(QThread):
    """ 爬取歌曲播放地址线程 """

    crawlFinished = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.playUrl = None
        self.coverPath = None
        self.songInfo = None
        self.quality = 'Standard quality'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
        self.crawler = KuWoMusicCrawler()

    def setSongInfo(self, songInfo: dict, quality='Standard quality'):
        """ 设置歌曲信息

        Parameters
        ----------
        songInfo: dict
            歌曲信息

        quality: str
            歌曲音质
        """
        self.quality = quality
        self.songInfo = songInfo

    def run(self):
        """ 根据歌曲 rid 爬取播放地址并下载封面 """
        AlbumCoverReader.coverFolder.mkdir(exist_ok=True, parents=True)

        # 爬取播放地址
        self.playUrl = self.crawler.getSongUrl(self.songInfo, self.quality)

        # 下载封面
        coverPath = ''
        folder = AlbumCoverReader.coverFolder/self.songInfo['coverName']
        names = [i.stem for i in folder.glob('*')]
        if self.songInfo['coverName'] not in names:
            coverPath = self.crawler.downloadAlbumCover(
                self.songInfo['coverPath'], self.songInfo['coverName'])

        self.coverPath = coverPath
        self.crawlFinished.emit(self.playUrl, coverPath)
