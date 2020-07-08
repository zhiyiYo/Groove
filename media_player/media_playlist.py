from random import shuffle

from PyQt5.Qt import QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlaylist


class MediaPlaylist(QMediaPlaylist):
    """ 播放列表类 """

    def __init__(self, parent=None, songPath_list: list = None):
        super().__init__(parent=parent)
        # 创建一个用于存储顺序播放列表的列表
        self.playlist = songPath_list
        # 初始化播放列表
        self.__initPlaylist()

    def __initPlaylist(self):
        """ 初始化播放列表 """
        # 设置播放模式为列表顺序播放
        self.setPlaybackMode(QMediaPlaylist.Sequential)
        # 确保播放列表是个列表
        if not self.playlist:
            self.playlist = []
        else:
            for songPath in self.playlist:
                self.addMedia(songPath)

    def addMedia(self, songPath:str):
        """ 重载addMedia,一次向尾部添加一首歌 """
        if not songPath:
            return
        self.playlist.append(songPath)
        super().addMedia(QMediaContent(QUrl.fromLocalFile(songPath)))

    def addMedias(self, songPath_list: list):
        """ 向尾部添加要播放的音频文件列表 """
        if not songPath_list:
            return
        self.playlist.extend(songPath_list)
        for songPath in songPath_list:
            self.addMedia(songPath)

    def insertMedias(self, index: int, songPath_list: list):
        """ 插入播放列表 """
        if not songPath_list:
            return
        self.playlist.insert(index, songPath_list)
        mediaContent_list = [QMediaContent(
            QUrl.fromLocalFile(songPath)) for songPath in songPath_list]
        self.insertMedia(index, mediaContent_list)
        
    def clear(self):
        """ 清空播放列表 """
        self.playlist.clear()
        super().clear()

    def next(self):
        """ 播放下一首 """
        # 如果已经是最后一首就转到第一首歌开始播放
        if self.currentIndex() == self.mediaCount() - 1:
            self.setCurrentIndex(0)
        else:
            super().next()

    def previous(self):
        """ 播放上一首 """
        # 如果是第一首就转到最后一首歌开始播放
        if self.currentIndex() == 0:
            self.setCurrentIndex(self.mediaCount() - 1)
        else:
            super().previous()
            
    def playThisSong(self, songPath:str):
        """ 按下歌曲卡的播放按钮或者双击歌曲卡时立即在当前的播放列表中播放这首歌 """
        if not songPath:
            return
        self.setCurrentIndex(self.playlist.index(songPath))

    def setRandomPlay(self):
        """ 进入随机播放模式 """
        if self.playlist:
            self.randomPlaylist = self.playlist.copy()
            shuffle(self.randomPlaylist)
