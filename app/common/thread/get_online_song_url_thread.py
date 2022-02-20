# coding:utf-8
from common.os_utils import getCoverName
from common.database.entity import SongInfo
from common.meta_data.reader import AlbumCoverReader
from common.crawler import KuWoMusicCrawler
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class GetOnlineSongUrlThread(QThread):
    """ Thread used to get the play url of online song """

    crawlFinished = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.playUrl = None
        self.coverPath = None
        self.songInfo = None
        self.quality = 'Standard quality'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
        self.crawler = KuWoMusicCrawler()

    def setSongInfo(self, songInfo: SongInfo, quality='Standard quality'):
        """ set song information for getting play url

        Parameters
        ----------
        songInfo: SongInfo
            song information

        quality: str
            song sound quality
        """
        self.quality = quality
        self.songInfo = songInfo

    def run(self):
        """ start to get play url """
        AlbumCoverReader.coverFolder.mkdir(exist_ok=True, parents=True)

        # get play url
        self.playUrl = self.crawler.getSongUrl(self.songInfo, self.quality)

        # download album cover
        coverPath = ''
        coverName = getCoverName(self.songInfo.singer, self.songInfo.album)
        folder = AlbumCoverReader.coverFolder / coverName
        names = [i.stem for i in folder.glob('*')]

        if coverName not in names or not list(folder.iterdir()):
            coverPath = self.crawler.downloadAlbumCover(
                self.songInfo['coverPath'], self.songInfo.singer, self.songInfo.album)

        self.coverPath = coverPath
        self.crawlFinished.emit(self.playUrl, coverPath)
