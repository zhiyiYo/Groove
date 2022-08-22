# coding:utf-8
import json
from pathlib import Path

from common.crawler import (KuGouMusicCrawler, KuWoMusicCrawler,
                            QQMusicCrawler, WanYiMusicCrawler)
from common.database.entity import SongInfo
from common.lyric import Lyric
from common.os_utils import adjustName
from PyQt5.QtCore import QThread, pyqtSignal


class GetLyricThread(QThread):
    """ Get lyrics thread """

    crawlFinished = pyqtSignal(Lyric)
    cacheFolder = Path('cache/lyric')

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.songInfo = None
        self.singer = ''
        self.songName = ''
        self.crawlers = [
            WanYiMusicCrawler(),
            KuWoMusicCrawler(),
            KuGouMusicCrawler(),
            QQMusicCrawler()
        ]

    def run(self):
        """ start to get lyric """
        self.cacheFolder.mkdir(exist_ok=True, parents=True)

        # search lyrics in local cached files
        path = self.getLyricPath()
        if path.exists():
            lyric = Lyric.load(path)
            if lyric.isValid():
                self.crawlFinished.emit(lyric)
                return

        # search lyrics online
        lyric = Lyric.new()
        keyWord = self.singer + ' ' + self.songName
        for crawler in self.crawlers:
            lyric_ = Lyric.parse(crawler.getLyric(keyWord))
            if lyric_.isValid():
                lyric_.save(path)
                lyric = lyric_
                break

        self.crawlFinished.emit(lyric)

    def get(self, songInfo: SongInfo):
        """ get lyrics """
        self.songInfo = songInfo
        self.singer = songInfo.singer
        self.songName = songInfo.title
        self.start()

    def reload(self):
        """ reload lyrics """
        path = self.getLyricPath()
        if path.exists():
            path.unlink()

        self.start()

    def getLyricPath(self):
        """ get lyric file path """
        file = adjustName(f'{self.singer}_{self.songName}.json')
        return self.cacheFolder / file
