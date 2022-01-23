# coding:utf-8
from pathlib import Path
from typing import List

from common.crawler.qq_music_crawler import QQMusicCrawler
from common.database.entity import SongInfo
from common.library import Directory
from common.meta_data.writer import writeAlbumCover, writeSongInfo
from common.os_utils import adjustName, isAudioFile
from PyQt5.QtCore import QThread, pyqtSignal


class GetFolderMetaDataThread(QThread):
    """ 获取文件夹中所有歌曲元数据的线程 """

    crawlSignal = pyqtSignal(str)
    cacheFolder = Path('cache/crawl_album_covers')

    def __init__(self, diretories: list, parent=None):
        super().__init__(parent=parent)
        self.__isStopped = False
        self.diretories = [Directory(i) for i in diretories]
        self.crawler = QQMusicCrawler()

    def run(self):
        """ 获取歌曲元数据 """
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
                # 修改歌曲信息
                songInfo.file = songPath
                writeSongInfo(songInfo)
                key = adjustName(songInfo["singer"] + '_' + songInfo['album'])

                # 从网上或者本地缓存文件夹获取专辑封面
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

            # 发送信号
            text = self.tr("Current progress: ")
            self.crawlSignal.emit(text+f"{(i+1)/len(songPaths):>3.0%}")

    def stop(self):
        """ 停止爬取歌曲信息 """
        self.__isStopped = True


class GetSongMetaDataThread(QThread):
    """ 获取一首歌曲元数据的线程 """

    crawlFinished = pyqtSignal(bool, SongInfo)
    cacheFolder = Path('cache/crawl_album_covers')

    def __init__(self, songPath: str, parent=None):
        """
        Parameters
        ----------
        songPath: str
            歌曲路径

        parent:
            父级
        """
        super().__init__(parent=parent)
        self.songPath = songPath
        self.crawler = QQMusicCrawler()

    def run(self):
        """ 爬取歌曲信息 """
        self.cacheFolder.mkdir(exist_ok=True, parents=True)

        songInfo = self.crawler.getSongInfo(Path(self.songPath).stem, 70)

        # 发送信号
        if not songInfo:
            self.crawlFinished.emit(False, SongInfo())
        else:
            songInfo.file = self.songPath

            # 获取专辑封面
            key = adjustName(songInfo.singer + '_' + songInfo.album)
            coverPath = self.cacheFolder / (key + '.jpg')
            url = self.crawler.getAlbumCoverURL(
                songInfo['albummid'], coverPath)
            if url:
                songInfo['coverPath'] = str(coverPath)

            self.crawlFinished.emit(True, songInfo)
