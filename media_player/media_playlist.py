from random import shuffle
from enum import Enum
from json import dump,load

from PyQt5.Qt import QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlaylist


class MediaPlaylist(QMediaPlaylist):
    """ 播放列表类 """
    # 当播放列表的当前下标变化时发送信号，用于更新主界面
    switchSongSignal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # 创建一个用于存储顺序播放列表的列表
        self.playlist = []
        # 保存当前的歌曲在随机播放列表中的下标
        self.currentRandomPlayIndex = 0
        # 初始化播放列表种类
        self.playlistType = PlaylistType(PlaylistType.LAST_PLAYLIST)
        # 初始化播放列表
        self.__initPlaylist()

    def __initPlaylist(self):
        """ 初始化播放列表 """
        # 设置播放模式为列表顺序播放
        self.setPlaybackMode(QMediaPlaylist.Sequential)
        # 记录下随机播放前的循环模式
        self.prePlayMode = self.playbackMode()
        # 初始化随机播放按钮按下状态
        self.randPlayBtPressed = False
        # 读入上次的播放列表
        self.readLastPlaylist()
        if self.playlist:
            for songInfo_dict in self.playlist:
                super().addMedia(QMediaContent(
                    QUrl.fromLocalFile(songInfo_dict['songPath'])))
        self.currentIndexChanged.connect(
            lambda index: self.switchSongSignal.emit(self.playlist[index]))

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
            super().addMedia(QMediaContent(
                QUrl.fromLocalFile(songInfo_dict['songPath'])))

    def insertMedia(self, index, songInfo_dict: dict):
        """ 在指定位置插入要播放的歌曲 """
        super().insertMedia(index, QMediaContent(
            QUrl.fromLocalFile(songInfo_dict['songPath'])))
        self.playlist.insert(index, songInfo_dict)

    def insertMedias(self, index: int, songInfoDict_list: list):
        """ 插入播放列表 """
        if not songInfoDict_list:
            return
        self.playlist = self.playlist[:index] + \
            songInfoDict_list + self.playlist[index:]
        mediaContent_list = [QMediaContent(
            QUrl.fromLocalFile(songInfo_dict['songPath'])) for songInfo_dict in songInfoDict_list]
        super().insertMedia(index, mediaContent_list)

    def clear(self):
        """ 清空播放列表 """
        self.playlist.clear()
        super().clear()

    def next(self):
        """ 播放下一首 """
        # 如果已经是最后一首就转到第一首歌开始播放
        if self.currentIndex() == self.mediaCount() - 1:
            # 列表循环时切换到第一首
            if self.playbackMode() == QMediaPlaylist.Loop:
                self.setCurrentIndex(0)
                # 切换歌曲时发出信号
                self.switchSongSignal.emit(self.playlist[self.currentIndex()])
            elif self.playbackMode() == QMediaPlaylist.Random:
                super().next()
        else:
            super().next()
            # 切换歌曲时发出信号
            self.switchSongSignal.emit(self.playlist[self.currentIndex()])

    def previous(self):
        """ 播放上一首 """
        # 如果是第一首就转到最后一首歌开始播放
        if self.currentIndex() == 0:
            if self.playbackMode() == QMediaPlaylist.Loop:
                self.setCurrentIndex(self.mediaCount() - 1)
                self.switchSongSignal.emit(self.playlist[self.currentIndex()])
        else:
            super().previous()
            self.switchSongSignal.emit(self.playlist[self.currentIndex()])

    def playThisSong(self, songInfo_dict: dict, newSongInfoDict_list: list = None, playlistType=0):
        """ 按下歌曲卡的播放按钮或者双击歌曲卡时立即在当前的播放列表中播放这首歌 """
        if not songInfo_dict:
            return
        # 更新播放列表种类和播放列表
        self.playlistType = PlaylistType(playlistType)
        if newSongInfoDict_list:
            self.setMedias(newSongInfoDict_list)
        # 设置当前播放歌曲
        if songInfo_dict in self.playlist:
            self.setCurrentIndex(self.playlist.index(songInfo_dict))
        else:
            # 如果这首歌不在播放列表中，就将其插入播放列表的表头
            self.insertMedia(0, songInfo_dict)
            self.setCurrentIndex(0)

    def playAlbum(self, songInfoDict_list: list):
        """ 播放专辑中的歌曲 """
        self.playlistType = PlaylistType.ALBUM_CARD_PLAYLIST
        self.setMedias(songInfoDict_list)

    def setRandomPlay(self, isRandomPlay=False):
        """ 按下随机播放按钮时根据循环模式决定是否设置随机播放模式 """
        if isRandomPlay:
            self.randPlayBtPressed = True
            # 记录按下随机播放前的循环模式
            self.prePlayMode = self.playbackMode()
            # 不处于单曲循环模式时就设置为随机播放
            if self.playbackMode() != QMediaPlaylist.CurrentItemInLoop:
                self.setPlaybackMode(QMediaPlaylist.Random)
        else:
            self.randPlayBtPressed = False
            # 恢复之前的循环模式
            self.setPlaybackMode(self.prePlayMode)

    def setMedias(self, songInfoDict_list: list):
        """ 重置播放列表 """
        self.clear()
        self.addMedias(songInfoDict_list)
        self.setCurrentIndex(0)

    def save(self):
        """ 保存关闭前的播放列表到json文件中 """
        with open('Data\\lastPlaylist.json', 'w', encoding='utf-8') as f:
            dump(self.playlist, f)
            
    def readLastPlaylist(self):
        """ 从json文件中读取播放列表 """
        try:
            with open('Data\\lastPlaylist.json',encoding='utf-8') as f:
                self.playlist = load(f)
        except:
            self.playlist = []

    def removeMedia(self, index):
        """ 在播放列表中移除歌曲 """
        currentIndex = self.currentIndex()
        if currentIndex > index:
            currentIndex -= 1
        self.playlist.pop(index)
        super().removeMedia(index)
        self.setCurrentIndex(currentIndex)


class PlaylistType(Enum):
    """ 播放列表种类枚举 """
    SONG_CARD_PLAYLIST = 0    # 播放列表为所有歌曲
    SONGER_CARD_PLAYLIST = 1  # 播放列表为选中歌手的歌
    ALBUM_CARD_PLAYLIST = 2   # 播放列表为选中专辑的歌
    LAST_PLAYLIST = 3         # 上一次的播放列表


if __name__ == "__main__":
    playlistType = PlaylistType(0)
    print(playlistType)
