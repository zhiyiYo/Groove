# coding:utf-8
from common.database.entity import SongInfo
from common.crawler import KuWoMusicCrawler, WanYiMusicCrawler
from PyQt5.QtCore import QThread, pyqtSignal


class GetSongDetailsUrlThread(QThread):
    """ get song details url thread """

    crawlFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.source = 'kuwo'
        self.songInfo = SongInfo()
        self.crawlers = {
            'kuwo': KuWoMusicCrawler(),
            'wanyi': WanYiMusicCrawler(),
        }

    def run(self):
        singer = self.songInfo.singer or ''
        songName = self.songInfo.title or ''
        keyWord = singer + ' ' + songName

        url = self.crawlers[self.source].getSongDetailsUrl(keyWord)
        self.crawlFinished.emit(url)

    def get(self, songInfo: SongInfo, source='kuwo'):
        """ get song details url

        Paramters
        ---------
        songInfo: SongInfo
            song information

        source: str
            the source song details url, could be `kuwo` or `wanyi`
        """
        self.songInfo = songInfo
        self.source = source
        self.start()
