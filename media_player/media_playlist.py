from random import shuffle

from PyQt5.Qt import QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlaylist


class MediaPlaylist(QMediaPlaylist):
    """ 播放列表类 """
    # 当点击上一首和下一首时发送信号
    switchSongSignal = pyqtSignal(dict)

    def __init__(self, parent=None, songInfoDict_list: list = None):
        super().__init__(parent=parent)
        # 创建一个用于存储顺序播放列表的列表
        self.playlist = songInfoDict_list
        # 保存当前的歌曲在随机播放列表中的下标
        self.currentRandomPlayIndex = 0
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
            for songInfo_dict in self.playlist:
                self.addMedia(songInfo_dict)
        self.currentPlaylist = self.playlist
        self.currentIndexChanged.connect(
            lambda index: self.switchSongSignal.emit(self.currentPlaylist[index]))
        

    def addMedia(self, songInfo_dict: dict):
        """ 重载addMedia,一次向尾部添加一首歌 """
        if not songInfo_dict:
            return
        self.playlist.append(songInfo_dict)
        super().addMedia(QMediaContent(
            QUrl.fromLocalFile(songInfo_dict['songPath'])))

    def addMedias(self, songInfoDict_list: list):
        """ 向尾部添加要播放的音频文件列表 """
        if not songInfoDict_list:
            return
        self.playlist.extend(songInfoDict_list)
        for songInfo_dict in songInfoDict_list:
            self.addMedia(songInfo_dict)

    def insertMedias(self, index: int, songInfoDict_list: list):
        """ 插入播放列表,updatePlaylist用来决定是否更新播放列表 """
        if not songInfoDict_list:
            return
        self.playlist.insert(index, songInfoDict_list)
        mediaContent_list = [QMediaContent(
            QUrl.fromLocalFile(songInfo_dict['songPath'])) for songInfo_dict in songInfoDict_list]
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
        self.switchSongSignal.emit(self.currentPlaylist[self.currentIndex()])

    def previous(self):
        """ 播放上一首 """
        # 如果是第一首就转到最后一首歌开始播放
        if self.currentIndex() == 0:
            self.setCurrentIndex(self.mediaCount() - 1)
        else:
            super().previous()
        self.switchSongSignal.emit(self.currentPlaylist[self.currentIndex()])

    def playThisSong(self, songInfo_dict: dict):
        """ 按下歌曲卡的播放按钮或者双击歌曲卡时立即在当前的播放列表中播放这首歌 """
        if not songInfo_dict:
            return
        self.setCurrentIndex(self.playlist.index(songInfo_dict))

    def setRandomPlay(self, isRandomPlay=False):
        """ 按下随机播放按钮设置随机播放模式 """
        
        if self.playlist:
            if isRandomPlay:
                self.randomPlaylist = self.playlist.copy()
                currentSong = self.randomPlaylist.pop(self.currentIndex())
                self.currentRandomPlayIndex = self.currentIndex()
                # 打乱剩下的列表然后重新组合
                shuffle(self.randomPlaylist)
                self.randomPlaylist.insert(self.currentIndex(), currentSong)
                self.currentPlaylist = self.randomPlaylist
            else:
                self.currentPlaylist = self.playlist
                

    

    