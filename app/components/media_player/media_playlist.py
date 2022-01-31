# coding:utf-8
import json
from enum import Enum
from pathlib import Path
from typing import List

from common.database.entity import SongInfo
from common.library import Library
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

    folder = Path('cache/last_playlist')

    def __init__(self, library: Library, parent=None):
        super().__init__(parent=parent)
        self.library = library
        self.playlist = []  # type:List[SongInfo]
        self.lastSongInfo = SongInfo()
        self.playlistType = PlaylistType(PlaylistType.LAST_PLAYLIST)

        self.setPlaybackMode(QMediaPlaylist.Sequential)
        self.prePlayMode = self.playbackMode()
        self.randPlayBtPressed = False
        self.__readLastPlaylist()

    def addSong(self, songInfo: SongInfo):
        """ 向播放列表末尾添加一首歌 """
        if not songInfo:
            return

        self.playlist.append(songInfo)
        super().addMedia(QMediaContent(QUrl(songInfo.file)))

    def addSongs(self, songInfos: list):
        """ 向播放列表尾部添加多首歌 """
        if not songInfos:
            return

        self.playlist.extend(songInfos)
        for songInfo in songInfos:
            super().addMedia(QMediaContent(QUrl(songInfo.file)))

    def insertSong(self, index: int, songInfo: SongInfo):
        """ 在指定位置插入要播放的歌曲 """
        super().insertMedia(
            index, QMediaContent(QUrl(songInfo.file)))
        self.playlist.insert(index, songInfo)

    def insertSongs(self, index: int, songInfos: List[SongInfo]):
        """ 插入播放列表 """
        if not songInfos:
            return

        self.playlist = self.playlist[:index] + \
            songInfos + self.playlist[index:]

        medias = [QMediaContent(QUrl(i.file)) for i in songInfos]
        super().insertMedia(index, medias)

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

    def getCurrentSong(self) -> SongInfo:
        """ 获取当前播放的歌曲信息 """
        if self.currentIndex() >= 0:
            return self.playlist[self.currentIndex()]

        return SongInfo(file='__invalid__')

    def setCurrentSong(self, songInfo: SongInfo):
        """ 按下歌曲卡的播放按钮或者双击歌曲卡时立即在当前的播放列表中播放这首歌 """
        if not songInfo:
            return

        self.setCurrentIndex(self.playlist.index(songInfo))

    def playAlbum(self, songInfos: List[SongInfo], index=0):
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

    def setPlaylist(self, songInfos: List[SongInfo], index=0):
        """ 设置歌曲播放列表 """
        if songInfos == self.playlist:
            return

        self.clear()
        self.addSongs(songInfos)
        self.setCurrentIndex(index)

    def save(self):
        """ 保存播放列表到json文件中 """
        self.folder.mkdir(exist_ok=True, parents=True)
        files = [i.file for i in self.playlist]
        playlist = {
            "files": files,
            "last": files[self.currentIndex()] if files else ''
        }
        with open(self.folder/'last_playlist.json', 'w', encoding='utf-8') as f:
            json.dump(playlist, f)

    def __readLastPlaylist(self):
        """ 读取上次的播放列表 """
        file = self.folder/"last_playlist.json"
        try:
            with open(file, encoding='utf-8') as f:
                playlist = json.load(f)
                files = playlist['files']
                last = playlist["last"]
        except:
            return

        self.playlist = self.library.songInfoController.getSongInfosByFile(
            files)
        self.lastSongInfo = self.library.songInfoController.getSongInfoByFile(
            last) or SongInfo()

        for songInfo in self.playlist:
            super().addMedia(QMediaContent(QUrl(songInfo.file)))

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

    def updateSongInfo(self, newSongInfo: SongInfo):
        """ 更新播放列表中一首歌曲的信息 """
        for i, songInfo in enumerate(self.playlist):
            if songInfo.file == newSongInfo.file:
                self.playlist[i] = newSongInfo

    def updateMultiSongInfos(self, songInfos: SongInfo):
        """ 更新播放列表中多首歌曲的信息 """
        for songInfo in songInfos:
            self.updateSongInfo(songInfo)
