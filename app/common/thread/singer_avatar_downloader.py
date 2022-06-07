# coding:utf-8
from typing import List, Union
from pathlib import Path

from common.os_utils import adjustName
from common.crawler import KuWoMusicCrawler, WanYiMusicCrawler
from common.signal_bus import signalBus
from PyQt5.QtCore import QRunnable, QThread, QThreadPool


class SingerAvatarDownloadWorker(QRunnable):
    """ Singer avatar download worker """

    def __init__(self, singers: List[str], saveDir: Union[str, Path]):
        """
        Parameters
        ----------
        singers: List[str]
            singer names

        saveDir: str or Path
            the root dir to save avatar
        """
        super().__init__()
        self.singers = singers or []
        self.saveDir = saveDir
        self.crawlers = [
            WanYiMusicCrawler(),
            KuWoMusicCrawler()
        ]

    def run(self):
        for singer in self.singers:
            for crawler in self.crawlers:
                save_path = crawler.getSingerAvatar(singer, self.saveDir)
                if save_path:
                    signalBus.downloadAvatarFinished.emit(singer, save_path)
                    break


class SingerAvatarDownloader:
    """ Singer avatar downloader """

    saveDir = Path('cache/singer_avatar')

    @classmethod
    def download(cls, singers: List[str]):
        """ download singer avatars

        Parameters
        ----------
        singers: List[str]
            singer names
        """
        singerMap = {adjustName(i): i for i in singers}

        # get singers that haven't been downloaded yet
        singerSet = set(singerMap.keys())
        downloaded = {i.name for i in cls.saveDir.glob('*') if i.is_dir()}
        toDownload = [singerMap[i] for i in singerSet-downloaded]
        toDownload.sort(key=lambda i: singers.index(i))

        # divide singers
        n = QThread.idealThreadCount()
        singerChunks = [toDownload[i:i+n]
                        for i in range(0, len(toDownload), n)]

        # download singer avatars
        pool = QThreadPool.globalInstance()
        for singerChunk in singerChunks:
            worker = SingerAvatarDownloadWorker(singerChunk, cls.saveDir)
            pool.start(worker)