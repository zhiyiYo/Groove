# coding:utf-8
import os
from copy import deepcopy
from enum import Enum
from json import dump, load

from app.common.os_utils import checkDirExists
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlaylist


class PlaylistType(Enum):
    """ 播放列表种类枚举 """

    SONG_CARD_PLAYLIST = 0  # 播放列表为一首歌
    SONGER_CARD_PLAYLIST = 1  # 播放列表为选中歌手的歌
    ALBUM_CARD_PLAYLIST = 2  # 播放列表为选中专辑的歌
    LAST_PLAYLIST = 3  # 上一次的播放列表
    NO_PLAYLIST = 4  # 没有播放列表
    CUSTOM_PLAYLIST = 5  # 自定义播放列表
    ALL_SONG_PLAYLIST = 6  # 播放列表为歌曲文件夹中的所有歌曲


class MediaPlaylist(QMediaPlaylist):
    """ 播放列表类 """

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
        self.__readLastPlaylist()
        if self.playlist:
            for songInfo_dict in self.playlist:
                super().addMedia(
                    QMediaContent(QUrl(songInfo_dict["songPath"])))

    def addMedia(self, songInfo_dict: dict):
        """ 重载addMedia,一次向尾部添加一首歌 """
        if not songInfo_dict:
            return
        self.playlist.append(songInfo_dict)
        super().addMedia(QMediaContent(
            QUrl(songInfo_dict["songPath"])))

    def addMedias(self, songInfo_list: list):
        """ 向尾部添加要播放的音频文件列表 """
        if not songInfo_list:
            return
        self.playlist.extend(songInfo_list)
        for songInfo_dict in songInfo_list:
            super().addMedia(
                QMediaContent(QUrl(songInfo_dict["songPath"])))

    def insertMedia(self, index, songInfo_dict: dict):
        """ 在指定位置插入要播放的歌曲 """
        super().insertMedia(
            index, QMediaContent(QUrl(songInfo_dict["songPath"])))
        self.playlist.insert(index, songInfo_dict)

    def insertMedias(self, index: int, songInfo_list: list):
        """ 插入播放列表 """
        if not songInfo_list:
            return
        self.playlist = self.playlist[:index] + \
            songInfo_list + self.playlist[index:]
        mediaContent_list = [
            QMediaContent(QUrl(songInfo_dict["songPath"]))
            for songInfo_dict in songInfo_list
        ]
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
            elif self.playbackMode() == QMediaPlaylist.Random:
                super().next()
        else:
            super().next()

    def previous(self):
        """ 播放上一首 """
        # 如果是第一首就转到最后一首歌开始播放
        if self.currentIndex() == 0:
            if self.playbackMode() == QMediaPlaylist.Loop:
                self.setCurrentIndex(self.mediaCount() - 1)
        else:
            super().previous()

    def getCurrentSong(self) -> dict:
        """ 获取当前播放的歌曲信息 """
        if self.currentIndex() >= 0:
            return self.playlist[self.currentIndex()]
        return {}

    def setCurrentSong(self, songInfo_dict: dict):
        """ 按下歌曲卡的播放按钮或者双击歌曲卡时立即在当前的播放列表中播放这首歌 """
        if not songInfo_dict:
            return
        # 设置当前播放歌曲
        self.setCurrentIndex(self.playlist.index(songInfo_dict))

    def playAlbum(self, songInfo_list: list, index=0):
        """ 播放专辑中的歌曲 """
        self.playlistType = PlaylistType.ALBUM_CARD_PLAYLIST
        self.setPlaylist(songInfo_list, index)

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

    def setPlaylist(self, songInfo_list: list, index=0):
        """ 重置播放列表 """
        if songInfo_list == self.playlist:
            return
        self.clear()
        self.addMedias(songInfo_list)
        self.setCurrentIndex(index)

    @checkDirExists('app/data')
    def save(self):
        """ 保存播放列表到json文件中 """
        playlistInfo = {
            "lastPlaylist": self.playlist,
            "lastSongInfo": self.getCurrentSong(),
        }
        with open("app/data/lastPlaylistInfo.json", "w", encoding="utf-8") as f:
            dump(playlistInfo, f)

    @checkDirExists('app/data')
    def __readLastPlaylist(self):
        """ 从json文件中读取播放列表 """
        try:
            with open("app/data/lastPlaylistInfo.json", encoding="utf-8") as f:
                playlistInfo = load(f)  # type:dict
                self.playlist = playlistInfo.get(
                    "lastPlaylist", [])  # type:list
                self.lastSongInfo = playlistInfo.get(
                    "lastSongInfo", {})  # type:dict

        except:
            self.playlist = []
            # 关闭窗口前正在播放的歌曲
            self.lastSongInfo = {}
        else:
            # 弹出已经不存在的歌曲
            if not os.path.exists(self.lastSongInfo.get("songPath", "")):
                self.lastSongInfo = {}
            for songInfo in deepcopy(self.playlist):
                if not os.path.exists(songInfo.get("songPath", "")):
                    self.playlist.remove(songInfo)

    def removeMedia(self, index):
        """ 在播放列表中移除歌曲 """
        currentIndex = self.currentIndex()
        if currentIndex >= index:
            currentIndex -= 1
        self.playlist.pop(index)
        super().removeMedia(index)
        self.setCurrentIndex(currentIndex)
        self.currentIndexChanged.emit(currentIndex)

    def updateOneSongInfo(self, newSongInfo: dict):
        """ 更新播放列表中一首歌曲的信息 """
        for i, songInfo in enumerate(self.playlist):
            if songInfo["songPath"] == newSongInfo["songPath"]:
                self.playlist[i] = newSongInfo

    def updateMultiSongInfo(self, newSongInfo_list: list):
        """ 更新播放列表中多首歌曲的信息 """
        for newSongInfo in newSongInfo_list:
            self.updateOneSongInfo(newSongInfo)
