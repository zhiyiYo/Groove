# coding:utf-8
from common.cache import lyricFolder
from common.config import config
from common.crawler import (KuGouMusicCrawler, KuWoMusicCrawler,
                            QQMusicCrawler, WanYiMusicCrawler)
from common.meta_data.reader import LyricReader
from common.database.entity import SongInfo
from common.lyric import Lyric
from PyQt5.QtCore import QThread, pyqtSignal


class GetLyricThread(QThread):
    """ Get lyrics thread """

    crawlFinished = pyqtSignal(Lyric)

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
        lyricFolder.mkdir(exist_ok=True, parents=True)

        if config.get(config.preferEmbedLyric):
            # use embedded lyrics
            lyric = LyricReader.read(self.songInfo.file)
            if not lyric.isValid():
                lyric = self.__getLyrics()
        else:
            # use online/local lyrics
            lyric = self.__getLyrics()
            if not lyric.isValid():
                lyric = LyricReader.read(self.songInfo.file)

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
        return Lyric.path(self.singer, self.songName)

    def __getLyrics(self):
        """ get lyrics from local lyrics file or online source """
        # search lyrics in local cached files
        path = self.getLyricPath()
        if path.exists():
            lyric = Lyric.load(path)
            if lyric.isValid():
                return lyric

        # search lyrics online
        lyric = Lyric.new()
        keyWord = self.singer + ' ' + self.songName
        for crawler in self.crawlers:
            lyric_ = Lyric.parse(crawler.getLyric(keyWord))
            if lyric_.isValid():
                lyric_.save(path)
                lyric = lyric_
                break

        return lyric
