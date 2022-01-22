# coding:utf-8
from pathlib import Path

from common.os_utils import isAudioFile
from common.meta_data.writer import writeAlbumCover, writeSongInfo
from common.crawler.qq_music_crawler import QQMusicCrawler
from PyQt5.QtCore import pyqtSignal, QThread


class GetFolderMetaDataThread(QThread):
    """ 获取文件夹中所有歌曲元数据的线程 """

    crawlSignal = pyqtSignal(str)
    cacheFolder = Path('cache/crawl_album_covers')

    def __init__(self, folderPaths: list, parent=None):
        super().__init__(parent=parent)
        self.__isStopped = False
        self.folderPaths = folderPaths
        self.crawler = QQMusicCrawler()

    def run(self):
        """ 获取歌曲元数据 """
        self.cacheFolder.mkdir(exist_ok=True, parents=True)
        albumCovers = {}

        songPaths, fileNames = self.__getAudioFiles()
        for i, (songPath, fileName) in enumerate(zip(songPaths, fileNames)):
            if self.__isStopped:
                break

            songInfo = self.crawler.getSongInfo(fileName)
            if songInfo:
                # 修改歌曲信息
                songInfo["songPath"] = songPath
                writeSongInfo(songInfo)
                key = songInfo["singer"] + '_' + songInfo['album']

                # 从网上或者本地缓存文件夹获取专辑封面
                if key not in albumCovers:
                    coverPath = str(self.cacheFolder/(key+'.jpg'))
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

    def __getAudioFiles(self):
        """ 获取音频文件路径和不包含后缀名的文件名

        Parameters
        ----------
        folderPaths: list
            文件夹列表

        Returns
        -------
        songPaths: list
            歌曲路径列表

        fileNames: list
            不含后缀名的歌曲文件名称列表
        """
        songPaths = []
        fileNames = []
        for folder in self.folderPaths:
            for file in Path(folder).glob('*'):
                if isAudioFile(file):
                    songPaths.append(str(file).replace('\\', '/'))
                    fileNames.append(file.stem)

        return songPaths, fileNames


class GetSongMetaDataThread(QThread):
    """ 获取一首歌曲元数据的线程 """

    crawlFinished = pyqtSignal(bool, dict)
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
            self.crawlFinished.emit(False, {})
        else:
            songInfo['songPath'] = self.songPath

            # 获取专辑封面
            key = songInfo["singer"] + '_' + songInfo['album']
            coverPath = self.cacheFolder / (key+'.jpg')
            url = self.crawler.getAlbumCoverURL(
                songInfo['albummid'], coverPath)
            if url:
                songInfo['coverPath'] = str(coverPath)

            self.crawlFinished.emit(True, songInfo)
