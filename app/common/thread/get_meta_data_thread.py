# coding:utf-8
from pathlib import Path
from typing import List

from common.cache import crawlAlbumCoverFolder
from common.crawler.qq_music_crawler import QQMusicCrawler
from common.database.entity import SongInfo
from common.library import Directory
from common.meta_data.writer import MetaDataWriter
from common.picture import Cover
from PyQt5.QtCore import QThread, pyqtSignal


class GetFolderMetaDataThread(QThread):
    """ Thread used to get all song meta data in directories """

    crawlSignal = pyqtSignal(str)

    def __init__(self, diretories: list, parent=None):
        super().__init__(parent=parent)
        self.__isStopped = False
        self.diretories = [Directory(i) for i in diretories]
        self.crawler = QQMusicCrawler()

    def run(self):
        """ start to crawl meta data """
        crawlAlbumCoverFolder.mkdir(exist_ok=True, parents=True)
        albumCovers = {}

        songPaths = []  # type:List[Path]
        for directory in self.diretories:
            songPaths.extend(directory.glob())

        writer = MetaDataWriter()
        for i, songPath in enumerate(songPaths):
            if self.__isStopped:
                break

            songInfo = self.crawler.getSongInfo(songPath.stem)
            if songInfo:
                # modify song information
                songInfo.file = songPath
                writer.writeSongInfo(songInfo)
                key = Cover(songInfo.singer, songInfo.album).name

                # search album cover in local or online
                if key not in albumCovers:
                    coverPath = str(crawlAlbumCoverFolder / (key + '.jpg'))
                    url = self.crawler.getAlbumCoverURL(
                        songInfo["albummid"], coverPath)
                    if url:
                        albumCovers[key] = coverPath
                        writer.writeAlbumCover(songPath, coverPath)
                else:
                    coverPath = albumCovers[key]
                    writer.writeAlbumCover(songPath, coverPath)

            # emit progress signal
            text = self.tr("Current progress: ")
            self.crawlSignal.emit(text+f"{(i+1)/len(songPaths):>3.0%}")

    def stop(self):
        """ stop crawling song information """
        self.__isStopped = True


class GetSongMetaDataThread(QThread):
    """ Thread used to get song meta data of one song """

    crawlFinished = pyqtSignal(bool, SongInfo)

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
        crawlAlbumCoverFolder.mkdir(exist_ok=True, parents=True)

        songInfo = self.crawler.getSongInfo(Path(self.songPath).stem, 70)

        if not songInfo:
            self.crawlFinished.emit(False, SongInfo())
        else:
            songInfo.file = self.songPath

            # get album cover
            key = Cover(songInfo.singer, songInfo.album).name
            coverPath = crawlAlbumCoverFolder / (key + '.jpg')
            url = self.crawler.getAlbumCoverURL(
                songInfo['albummid'], coverPath)
            if url:
                songInfo['coverPath'] = str(coverPath)

            self.crawlFinished.emit(True, songInfo)
