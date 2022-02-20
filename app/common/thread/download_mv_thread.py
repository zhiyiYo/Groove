# coding:utf-8
from queue import Queue
from urllib.request import urlretrieve
from PyQt5.QtCore import pyqtSignal, QThread


class DownloadMvThread(QThread):
    """ Download MV thread """

    downloadOneMvFinished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.download_queque = Queue()

    def run(self):
        """ start to download MV """
        while not self.download_queque.empty():
            url, save_path = self.download_queque.get()
            urlretrieve(url, save_path)
            self.downloadOneMvFinished.emit()

    def appendDownloadTask(self, url: str, save_path: str):
        """ add download task to queque """
        self.download_queque.put((url, save_path))
