# coding:utf-8
from pathlib import Path
from typing import List

from common.crawler.qq_music_crawler import QQMusicCrawler
from common.database.entity import SongInfo
from common.library import Directory
from common.meta_data.writer import writeAlbumCover, writeSongInfo
from common.os_utils import getCoverName
from PyQt5.QtCore import QThread, pyqtSignal


class GetFolderMetaDataThread(QThread):
    """ Thread used to get all song meta data in directories """

    crawlSignal = pyqtSignal(str)
    cacheFolder = Path('cache/crawl_album_covers')

    def __init__(self, diretories: list, parent=None):
        super().__init__(parent=parent)
        self.__isStopped = False
        self.diretories = [Directory(i) for i in diretories]
        self.crawler = QQMusicCrawler()

    def run(self):
        """ start to crawl meta data """
        self.cacheFolder.mkdir(exist_ok=True, parents=True)
        albumCovers = {}

        songPaths = []  # type:List[Path]
        for directory in self.diretories:
            songPaths.extend(directory.glob())

        for i, songPath in enumerate(songPaths):
            if self.__isStopped:
                break

            songInfo = self.crawler.getSongInfo(songPath.stem)
            if songInfo:
                # modify song information
                songInfo.file = songPath
                writeSongInfo(songInfo)
                key = getCoverName(songInfo.singer, songInfo.album)

                # search album cover in local or online
                if key not in albumCovers:
                    coverPath = str(self.cacheFolder / (key + '.jpg'))
                    url = self.crawler.getAlbumCoverURL(
                        songInfo["albummid"], coverPath)
                    if url:
                        albumCovers[key] = coverPath
                        writeAlbumCover(songPath, coverPath)
                else:
                    coverPath = albumCovers[key]
                    writeAlbumCover(songPath, coverPath)

            # emit progress signal
            text = self.tr("Current progress: ")
            self.crawlSignal.emit(text+f"{(i+1)/len(songPaths):>3.0%}")

    def stop(self):
        """ stop crawling song information """
        self.__isStopped = True


class GetSongMetaDataThread(QThread):
    """ Thread used to get song meta data of one song """

    crawlFinished = pyqtSignal(bool, SongInfo)
    cacheFolder = Path('cache/crawl_album_covers')

    def __init__(self, songPath: str, parent=None):
        """
        Parameters
        ----------
        songPath: str
            audio file path

        parent:
            parent instance
        """
        super().__init__(parent=parent)
        self.songPath = songPath
        self.crawler = QQMusicCrawler()

    def run(self):
        """ start to crawl song information """
        self.cacheFolder.mkdir(exist_ok=True, parents=True)

        songInfo = self.crawler.getSongInfo(Path(self.songPath).stem, 70)

        if not songInfo:
            self.crawlFinished.emit(False, SongInfo())
        else:
            songInfo.file = self.songPath

            # get album cover
            key = getCoverName(songInfo.singer, songInfo.album)
            coverPath = self.cacheFolder / (key + '.jpg')
            url = self.crawler.getAlbumCoverURL(
                songInfo['albummid'], coverPath)
            if url:
                songInfo['coverPath'] = str(coverPath)

            self.crawlFinished.emit(True, songInfo)
