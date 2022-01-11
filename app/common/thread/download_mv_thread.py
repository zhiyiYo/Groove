# coding:utf-8
from queue import Queue
from urllib.request import urlretrieve
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class DownloadMvThread(QThread):
    """ 下载 MV 线程 """

    downloadOneMvFinished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.download_queque = Queue()    # 下载队列

    def run(self):
        """ 下载 MV """
        while not self.download_queque.empty():
            url, save_path = self.download_queque.get()
            urlretrieve(url, save_path)
            self.downloadOneMvFinished.emit()

    def appendDownloadTask(self, url: str, save_path: str):
        """ 添加下载任务 """
        self.download_queque.put((url, save_path))
