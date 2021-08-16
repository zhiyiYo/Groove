# coding:utf-8
import os
from queue import Queue

from app.common.crawler.kuwo_music_crawler import KuWoMusicCrawler
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap


class DownloadSongThread(QThread):

    def __init__(self, saveDir, parent=None):
        super().__init__(parent=parent)
        self.saveDir = saveDir
        self.crawler = KuWoMusicCrawler()
        self.download_queque = Queue()    # 下载队列，内含 songInfo

    def run(self):
        """ 下载歌曲 """
        os.makedirs(self.saveDir, exist_ok=True)
        while not self.download_queque.empty():
            songInfo, quality = self.download_queque.get()
            path = self.crawler.downloadSong(songInfo, self.saveDir, quality)
            print(f'下载 {path} 完毕！')

        print('完成所有下载任务')

    def appendDownloadTask(self, songInfo: dict, quality='流畅音质'):
        """ 添加下载任务 """
        self.download_queque.put((songInfo, quality))
