# coding:utf-8
from pathlib import Path
from common.config import config
from common.crawler import KuWoMusicCrawler
from common.database.entity import SongInfo
from common.picture import Cover
from PyQt5.QtCore import QThread, pyqtSignal


class GetOnlineSongUrlThread(QThread):
    """ Thread used to get the play url of online song """

    crawlFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.playUrl = None
        self.coverPath = None
        self.songInfo = None    # type: SongInfo
        self.crawler = KuWoMusicCrawler()

    def run(self):
        """ start to get play url """
        # get play url
        self.playUrl = self.crawler.getSongUrl(
            self.songInfo, config.get(config.onlineSongQuality))

        # download album cover
        songInfo = self.songInfo
        cover = Cover(songInfo.singer, songInfo.album)
        self.coverPath = cover.path()
        if self.coverPath.startswith(":") or not Path(self.coverPath).exists():
            url = self.songInfo.get('coverPath') or \
                self.crawler.getAlbumCoverUrl(songInfo.singer+" "+songInfo.title)
            self.coverPath = self.crawler.downloadAlbumCover(
                url, self.songInfo.singer, self.songInfo.album)

        self.crawlFinished.emit(self.playUrl)

    def search(self, songInfo: SongInfo):
        """ search song url """
        self.songInfo = songInfo
        self.start()
