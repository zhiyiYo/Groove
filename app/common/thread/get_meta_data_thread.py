# coding:utf-8
import os

from common.meta_data_writer import writeAlbumCover, writeSongInfo
from common.crawler.qq_music_crawler import QQMusicCrawler
from PyQt5.QtCore import pyqtSignal, QThread


class GetMetaDataThread(QThread):
    """ 获取歌曲元数据线程 """

    crawlSignal = pyqtSignal(str)

    def __init__(self, folderPaths: list, parent=None):
        super().__init__(parent=parent)
        self.__isStopped = False
        self.folderPaths = folderPaths
        self.crawler = QQMusicCrawler()

    def run(self):
        """ 获取歌曲元数据 """
        # 创建一个本地专辑封面缓存文件夹
        cover_folder = 'crawl_album_covers'
        os.makedirs(cover_folder, exist_ok=True)
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
                key = songInfo["singer"]+'_'+songInfo['album']

                # 从网上或者本地缓存文件夹获取专辑封面
                if key not in albumCovers:
                    coverPath = f'{cover_folder}/{key}.jpg'
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
        for folderPath in self.folderPaths:
            files = os.listdir(folderPath)
            for file in files:
                if file.endswith(('.mp3', '.flac', '.m4a')):
                    songPaths.append(os.path.join(
                        folderPath, file).replace('\\', '/'))
                    fileNames.append(os.path.splitext(file)[0])

        return songPaths, fileNames
