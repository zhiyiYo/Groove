# coding:utf-8
import os
from copy import deepcopy
from enum import Enum
from json import dump, load

from common.os_utils import checkDirExists
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlaylist


class PlaylistType(Enum):
    """ 播放列表种类枚举 """

    SONG_CARD_PLAYLIST = 0      # 播放列表为一首歌
    SONGER_CARD_PLAYLIST = 1    # 播放列表为选中歌手的歌
    ALBUM_CARD_PLAYLIST = 2     # 播放列表为选中专辑的歌
    LAST_PLAYLIST = 3           # 上一次的播放列表
    NO_PLAYLIST = 4             # 没有播放列表
    CUSTOM_PLAYLIST = 5         # 自定义播放列表
    ALL_SONG_PLAYLIST = 6       # 播放列表为歌曲文件夹中的所有歌曲


class MediaPlaylist(QMediaPlaylist):
    """ 播放列表类 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.playlist = []
        self.playlistType = PlaylistType(PlaylistType.LAST_PLAYLIST)

        self.setPlaybackMode(QMediaPlaylist.Sequential)
        self.prePlayMode = self.playbackMode()
        self.randPlayBtPressed = False
        self.__readLastPlaylist()

        if self.playlist:
            for songInfo in self.playlist:
                super().addMedia(QMediaContent(QUrl(songInfo["songPath"])))

    def addSong(self, songInfo: dict):
        """ 向播放列表末尾添加一首歌 """
        if not songInfo:
            return

        self.playlist.append(songInfo)
        super().addMedia(QMediaContent(
            QUrl(songInfo["songPath"])))

    def addSongs(self, songInfos: list):
        """ 向播放列表尾部添加多首歌 """
        if not songInfos:
            return

        self.playlist.extend(songInfos)
        for songInfo in songInfos:
            super().addMedia(QMediaContent(QUrl(songInfo["songPath"])))

    def insertSong(self, index: int, songInfo: dict):
        """ 在指定位置插入要播放的歌曲 """
        super().insertMedia(
            index, QMediaContent(QUrl(songInfo["songPath"])))
        self.playlist.insert(index, songInfo)

    def insertSongs(self, index: int, songInfos: list):
        """ 插入播放列表 """
        if not songInfos:
            return

        self.playlist = self.playlist[:index] + \
            songInfos + self.playlist[index:]
        mediaContent_list = [
            QMediaContent(QUrl(i["songPath"])) for i in songInfos]
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
            if self.playbackMode() == QMediaPlaylist.CurrentItemInLoop:
                self.setCurrentIndex(self.currentIndex()+1)
            else:
                super().next()

    def previous(self):
        """ 播放上一首 """
        # 如果是第一首就转到最后一首歌开始播放
        if self.currentIndex() == 0:
            if self.playbackMode() == QMediaPlaylist.Loop:
                self.setCurrentIndex(self.mediaCount() - 1)
        else:
            if self.playbackMode() == QMediaPlaylist.CurrentItemInLoop:
                self.setCurrentIndex(self.currentIndex()-1)
            else:
                super().previous()

    def getCurrentSong(self) -> dict:
        """ 获取当前播放的歌曲信息 """
        if self.currentIndex() >= 0:
            return self.playlist[self.currentIndex()]

        return {}

    def setCurrentSong(self, songInfo: dict):
        """ 按下歌曲卡的播放按钮或者双击歌曲卡时立即在当前的播放列表中播放这首歌 """
        if not songInfo:
            return

        self.setCurrentIndex(self.playlist.index(songInfo))

    def playAlbum(self, songInfos: list, index=0):
        """ 播放专辑中的歌曲 """
        self.playlistType = PlaylistType.ALBUM_CARD_PLAYLIST
        self.setPlaylist(songInfos, index)

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

    def setPlaylist(self, songInfos: list, index=0):
        """ 设置歌曲播放列表 """
        if songInfos == self.playlist:
            return

        self.clear()
        self.addSongs(songInfos)
        self.setCurrentIndex(index)

    @checkDirExists('cache/song_info')
    def save(self):
        """ 保存播放列表到json文件中 """
        playlistInfo = {
            "lastPlaylist": self.playlist,
            "lastSongInfo": self.getCurrentSong(),
        }
        with open("cache/song_info/lastPlaylistInfo.json", "w", encoding="utf-8") as f:
            dump(playlistInfo, f)

    @checkDirExists('cache/song_info')
    def __readLastPlaylist(self):
        """ 从json文件中读取播放列表 """
        try:
            with open("cache/song_info/lastPlaylistInfo.json", encoding="utf-8") as f:
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

    def removeSong(self, index):
        """ 在播放列表中移除歌曲 """
        currentIndex = self.currentIndex()
        if currentIndex >= index:
            currentIndex -= 1

        self.playlist.pop(index)
        super().removeMedia(index)
        self.setCurrentIndex(currentIndex)

    def removeOnlineSong(self, index: int):
        """ 移除在线歌曲 """
        self.playlist.pop(index)
        super().removeMedia(index)

    def updateOneSongInfo(self, newSongInfo: dict):
        """ 更新播放列表中一首歌曲的信息 """
        for i, songInfo in enumerate(self.playlist):
            if songInfo["songPath"] == newSongInfo["songPath"]:
                self.playlist[i] = newSongInfo

    def updateMultiSongInfo(self, newSongInfo_list: list):
        """ 更新播放列表中多首歌曲的信息 """
        for newSongInfo in newSongInfo_list:
            self.updateOneSongInfo(newSongInfo)
