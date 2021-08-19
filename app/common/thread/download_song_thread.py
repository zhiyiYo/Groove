# coding:utf-8
import os
from queue import Queue

from app.common.crawler.kuwo_music_crawler import KuWoMusicCrawler
from PyQt5.QtCore import QThread, pyqtSignal


class DownloadSongThread(QThread):

    downloadOneSongCompleteSig = pyqtSignal()

    def __init__(self, downloadFolder: str, parent=None):
        super().__init__(parent=parent)
        self.downloadFolder = downloadFolder
        self.crawler = KuWoMusicCrawler()
        self.download_queque = Queue()    # 下载队列，内含 songInfo

    def run(self):
        """ 下载歌曲 """
        os.makedirs(self.downloadFolder, exist_ok=True)

        while not self.download_queque.empty():
            songInfo, quality = self.download_queque.get()

            # 发送下载音乐请求
            self.crawler.downloadSong(songInfo, self.downloadFolder, quality)

            # 发送完成一首歌下载信号
            self.downloadOneSongCompleteSig.emit()

    def appendDownloadTask(self, songInfo: dict, quality='流畅音质'):
        """ 添加下载任务 """
        self.download_queque.put((songInfo, quality))
