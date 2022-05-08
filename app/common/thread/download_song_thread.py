# coding:utf-8
import os
from queue import Queue

from common.config import config
from common.database.entity import SongInfo
from common.crawler import KuWoMusicCrawler
from PyQt5.QtCore import QThread, pyqtSignal


class DownloadSongThread(QThread):
    """ Download song thread """

    downloadOneSongFinished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.crawler = KuWoMusicCrawler()
        self.queue = Queue()

    def run(self):
        """ start to download song """
        folder = config['download-folder']
        os.makedirs(folder, exist_ok=True)

        while not self.queue.empty():
            songInfo, quality = self.queue.get()

            # send request to download song
            self.crawler.downloadSong(songInfo, folder, quality)

            self.downloadOneSongFinished.emit()

    def appendDownloadTask(self, songInfo: SongInfo, quality='Standard quality'):
        """ add download task to queque """
        self.queue.put((songInfo, quality))
