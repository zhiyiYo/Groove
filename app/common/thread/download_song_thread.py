# coding:utf-8
import os
from queue import Queue

from common.database.entity import SongInfo
from common.crawler import KuWoMusicCrawler
from PyQt5.QtCore import QThread, pyqtSignal


class DownloadSongThread(QThread):
    """ Download song thread """

    downloadOneSongFinished = pyqtSignal()

    def __init__(self, downloadFolder: str, parent=None):
        super().__init__(parent=parent)
        self.downloadFolder = downloadFolder
        self.crawler = KuWoMusicCrawler()
        self.download_queque = Queue()

    def run(self):
        """ start to download song """
        os.makedirs(self.downloadFolder, exist_ok=True)

        while not self.download_queque.empty():
            songInfo, quality = self.download_queque.get()

            # send request to download song
            self.crawler.downloadSong(songInfo, self.downloadFolder, quality)

            self.downloadOneSongFinished.emit()

    def appendDownloadTask(self, songInfo: SongInfo, quality='Standard quality'):
        """ add download task to queque """
        self.download_queque.put((songInfo, quality))
