# coding:utf-8
from common.cache import albumCoverFolder
from common.config import config
from common.crawler import KuWoMusicCrawler
from common.database.entity import SongInfo
from common.os_utils import getCoverName
from PyQt5.QtCore import QThread, pyqtSignal


class GetOnlineSongUrlThread(QThread):
    """ Thread used to get the play url of online song """

    crawlFinished = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.playUrl = None
        self.coverPath = None
        self.songInfo = None    # type: SongInfo
        self.crawler = KuWoMusicCrawler()

    def run(self):
        """ start to get play url """
        albumCoverFolder.mkdir(exist_ok=True, parents=True)

        # get play url
        self.playUrl = self.crawler.getSongUrl(
            self.songInfo, config.get(config.onlineSongQuality))

        # download album cover
        coverPath = ''
        coverName = getCoverName(self.songInfo.singer, self.songInfo.album)
        folder = albumCoverFolder / coverName
        names = [i.stem for i in folder.glob('*')]

        if coverName not in names or not list(folder.iterdir()):
            coverPath = self.crawler.downloadAlbumCover(
                self.songInfo['coverPath'], self.songInfo.singer, self.songInfo.album)

        self.coverPath = coverPath
        self.crawlFinished.emit(self.playUrl, coverPath)

    def search(self, songInfo: SongInfo):
        """ search song url """
        self.songInfo = songInfo
        self.start()
