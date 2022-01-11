# coding:utf-8
import json
from pathlib import Path

from common.crawler import KuWoMusicCrawler, KuGouMusicCrawler, WanYiMusicCrawler
from common.lyric_parser import parse_lyric
from common.os_utils import adjustName
from PyQt5.QtCore import QThread, pyqtSignal


class GetLyricThread(QThread):
    """ 获取歌词线程 """

    crawlFinished = pyqtSignal(dict)
    cacheFolder = Path('cache/lyric')

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.singer = ''
        self.songName = ''
        self.crawlers = [
            KuWoMusicCrawler(),
            WanYiMusicCrawler(),
            KuGouMusicCrawler()
        ]

    def run(self):
        """ 搜索歌词 """
        self.cacheFolder.mkdir(exist_ok=True, parents=True)

        # 在本地缓存中寻找文件
        file = adjustName(f'{self.singer}_{self.songName}.json')
        lyricPath = self.cacheFolder / file
        if lyricPath.exists():
            with open(lyricPath, 'r', encoding='utf-8') as f:
                self.crawlFinished.emit(json.load(f))
                return

        # 搜索歌词
        notEmpty = False
        keyWord = self.singer + ' ' + self.songName

        for crawler in self.crawlers:
            lyric = crawler.getLyric(keyWord)
            notEmpty = bool(lyric)
            if notEmpty:
                break

        lyric = parse_lyric(lyric)

        # 保存歌词文件
        if notEmpty:
            with open(lyricPath, 'w', encoding='utf-8') as f:
                json.dump(lyric, f)

        self.crawlFinished.emit(lyric)

    def setSongInfo(self, songInfo: dict):
        """ 设置歌曲信息 """
        self.singer = songInfo['singer']
        self.songName = songInfo['songName']
