# coding:utf-8
import json
from pathlib import Path

from common.database.entity import SongInfo
from common.crawler import KuWoMusicCrawler, KuGouMusicCrawler, WanYiMusicCrawler, QQMusicCrawler
from common.lyric_parser import parse_lyric, LyricParserBase
from common.os_utils import adjustName
from PyQt5.QtCore import QThread, pyqtSignal


class GetLyricThread(QThread):
    """ Get lyrics thread """

    crawlFinished = pyqtSignal(dict)
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
        lyricPath = self.getLyricPath()
        if lyricPath.exists():
            with open(lyricPath, 'r', encoding='utf-8') as f:
                self.crawlFinished.emit(json.load(f))
                return

        # search lyrics online
        notEmpty = False
        keyWord = self.singer + ' ' + self.songName

        for crawler in self.crawlers:
            lyric = crawler.getLyric(keyWord)
            notEmpty = bool(lyric)
            if notEmpty and parse_lyric(lyric) != LyricParserBase.error_lyric:
                break

        lyric = parse_lyric(lyric)

        # cache lyrics to local
        if notEmpty:
            with open(lyricPath, 'w', encoding='utf-8') as f:
                json.dump(lyric, f, ensure_ascii=False, indent=4)

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
