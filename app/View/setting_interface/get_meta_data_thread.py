# coding:utf-8
import os

from app.common.write_album_cover import writeAlbumCover
from app.common.modify_song_info import modifySongInfo
from app.common.crawler.qq_music_crawler import QQMusicCrawler
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class GetMetaDataThread(QThread):
    """ 获取歌曲元数据线程 """

    crawlSignal = pyqtSignal(str)

    def __init__(self, folderPaths: list, parent=None):
        super().__init__(parent=parent)
        self.folderPaths = folderPaths
        self.crawler = QQMusicCrawler()

    def run(self):
        """ 获取歌曲元数据 """
        # 创建一个本地专辑封面缓存文件夹
        cover_folder = 'app/resource/crawl_album_covers'
        os.makedirs(cover_folder, exist_ok=True)
        albumCovers = {}

        songPaths, fileNames = self.__getAudioFiles()
        for i, (songPath, fileName) in enumerate(zip(songPaths, fileNames)):
            songInfo = self.crawler.getSongInfo(fileName)
            if songInfo:
                # 修改歌曲信息
                songInfo["songPath"] = songPath
                modifySongInfo(songInfo)
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
            self.crawlSignal.emit(f"当前进度：{(i+1)/len(songPaths):>3.0%}")

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
                    songPaths.append(os.path.join(folderPath, file))
                    fileNames.append(os.path.splitext(file)[0])

        return songPaths, fileNames
