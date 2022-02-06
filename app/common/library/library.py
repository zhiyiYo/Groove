# coding:utf-8
from pathlib import Path
from typing import List

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtSql import QSqlDatabase

from ..database.entity import SongInfo
from ..database.controller import (AlbumCoverController, AlbumInfoController,
                                   PlaylistController, SingerInfoController,
                                   SongInfoController)
from .file_system import FileSystem


class Library(QObject):
    """ 歌曲库 """

    loadFinished = pyqtSignal()
    reloadFinished = pyqtSignal()
    fileAdded = pyqtSignal(list)
    fileRemoved = pyqtSignal(list)

    cacheFile = 'cache/cache.db'

    def __init__(self, directories: List[str] = None, db: QSqlDatabase = None, watch=True, parent=None):
        """
        Parameters
        ----------
        directories: List[str]
            歌曲文件夹列表

        db: QDataBase
            使用的数据库

        watch: bool
            是否监视文件夹

        parent:
            父级
        """
        super().__init__(parent=parent)
        self.songInfos = []
        self.albumInfos = []
        self.singerInfos = []
        self.playlists = []
        self.directories = directories
        self.fileSystem = FileSystem(directories, self)

        self.songInfoController = SongInfoController(db)
        self.albumInfoController = AlbumInfoController(db)
        self.albumCoverController = AlbumCoverController()
        self.singerInfoController = SingerInfoController(db)
        self.playlistController = PlaylistController(db)

        if watch:
            self.fileSystem.added.connect(self.__onFileAdded)
            self.fileSystem.removed.connect(self.__onFileRemoved)

    def load(self):
        """ 载入歌曲信息 """
        files = self.fileSystem.glob()
        self.songInfos = self.songInfoController.getSongInfosFromCache(files)
        self.albumInfos = self.albumInfoController.getAlbumInfosFromCache(
            self.songInfos)
        self.albumCoverController.getAlbumCovers(self.songInfos)
        self.singerInfos = self.singerInfoController.getSingerInfosFromCache(
            self.albumInfos)
        self.playlists = self.playlistController.getAllPlaylists()

        self.loadFinished.emit()

    def setDirectories(self, directories: List[str]):
        """ 设置歌曲文件目录 """
        isChanged = self.fileSystem.setDirs(directories)

        if not isChanged:
            self.reloadFinished.emit()
            return

        self.directories = directories

        # 更新信息列表和数据库
        self.load()

        self.reloadFinished.emit()

    def initDatabase(self):
        """ 初始化数据库 """
        self.songInfoController.songInfoService.createTable()
        self.albumInfoController.albumInfoService.createTable()

    def setDatabase(self, db: QSqlDatabase):
        """ 设置数据库 """
        self.songInfoController.songInfoService.setDatabase(db)
        self.albumInfoController.albumInfoService.setDatabase(db)
        self.singerInfoController.singerInfoService.setDatabase(db)

    def copyTo(self, library):
        """ 拷贝歌曲库的信息 """
        library.songInfos = self.songInfos
        library.albumInfos = self.albumInfos
        library.singerInfos = self.singerInfos
        library.playlists = self.playlists
        library.directories = self.directories.copy()
        library.fileSystem.setDirs(self.directories)

    def updateSongInfo(self, songInfo: SongInfo):
        """ 更新一首歌曲信息 """
        self.songInfoController.updateSongInfo(songInfo)

        for i, songInfo_ in enumerate(self.songInfos):
            if songInfo.file == songInfo_.file:
                self.songInfos[i] = songInfo
                break

        self.albumInfos = self.albumInfoController.getAlbumInfosFromCache(
            self.songInfos)
        self.singerInfos = self.singerInfoController.getSingerInfosFromCache(
            self.albumInfos)

    def updateMultiSongInfos(self, songInfos: List[SongInfo]):
        """ 更新多首歌曲信息 """
        self.songInfoController.updateMultiSongInfos(songInfos)

        songInfoMap = {i.file: i for i in songInfos}
        for i, songInfo_ in enumerate(self.songInfos):
            if songInfo_.file in songInfoMap:
                self.songInfos[i] = songInfoMap[songInfo_.file]

        self.albumInfos = self.albumInfoController.getAlbumInfosFromCache(
            self.songInfos)
        self.singerInfos = self.singerInfoController.getSingerInfosFromCache(
            self.albumInfos)

    def __onFileAdded(self, files: List[Path]):
        """ 增加歌曲文件槽函数 """
        songInfos = self.songInfoController.addSongInfos(files)

        self.songInfos.extend(songInfos)
        self.songInfos.sort(key=lambda i: i.modifiedTime, reverse=True)
        self.albumInfos = self.albumInfoController.getAlbumInfosFromCache(
            self.songInfos)
        self.singerInfos = self.singerInfoController.getSingerInfosFromCache(
            self.albumInfos)

        self.fileAdded.emit(songInfos)

    def __onFileRemoved(self, files: List[Path]):
        """ 移除歌曲文件槽函数 """
        files = self.songInfoController.removeSongInfos(files)

        for songInfo in self.songInfos.copy():
            if songInfo.file in files:
                self.songInfos.remove(songInfo)

        self.albumInfos = self.albumInfoController.getAlbumInfosFromCache(
            self.songInfos)
        self.singerInfos = self.singerInfoController.getSingerInfosFromCache(
            self.albumInfos)

        self.fileRemoved.emit(files)
