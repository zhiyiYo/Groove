# coding:utf-8
from pathlib import Path
from typing import List, Union

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtSql import QSqlDatabase

from ..database.controller import (AlbumCoverController, AlbumInfoController,
                                   PlaylistController, RecentPlayController,
                                   SingerInfoController, SongInfoController)
from ..database.entity import SongInfo
from .file_system import FileSystem


class Library(QObject):
    """ Song library """

    loadFinished = pyqtSignal()
    reloadFinished = pyqtSignal()
    fileAdded = pyqtSignal(list)
    fileRemoved = pyqtSignal(list)
    loadFromFilesFinished = pyqtSignal(list)

    cacheFile = 'cache/cache.db'

    def __init__(self, directories: List[str] = None, db: QSqlDatabase = None, watch=True, parent=None):
        """
        Parameters
        ----------
        directories: List[str]
            audio directories

        db: QDataBase
            database to be used

        watch: bool
            whether to monitor audio directories

        parent:
            parent instance
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
        self.recentPlayController = RecentPlayController(db)

        self.songInfos = []
        self.albumInfos = []
        self.singerInfos = []
        self.playlists = []
        self.recentPlaySongInfos = []

        if watch:
            self.fileSystem.added.connect(self.__onFileAdded)
            self.fileSystem.removed.connect(self.__onFileRemoved)

    def load(self):
        """ load data to library """
        files = self.fileSystem.glob()
        self.songInfos = self.songInfoController.getSongInfosFromCache(files)
        self.albumInfos = self.albumInfoController.getAlbumInfosFromCache(
            self.songInfos)
        self.albumCoverController.getAlbumCovers(self.songInfos)
        self.singerInfos = self.singerInfoController.getSingerInfosFromCache(
            self.albumInfos)
        self.playlists = self.playlistController.getAllPlaylists()
        self.recentPlaySongInfos = self.recentPlayController.getRecentPlays()

        self.loadFinished.emit()

    def loadFromFiles(self, files: List[Union[Path, str]]):
        """ load song information from files """
        songInfos = self.songInfoController.getSongInfosFromFile(files)
        self.albumCoverController.getAlbumCovers(songInfos)
        self.loadFromFilesFinished.emit(songInfos)
        return songInfos

    def setDirectories(self, directories: List[str]):
        """ set the audio directories """
        isChanged = self.fileSystem.setDirs(directories)

        if not isChanged:
            self.reloadFinished.emit()
            return

        self.directories = directories

        # update library
        self.load()

        self.reloadFinished.emit()

    def setDatabase(self, db: QSqlDatabase):
        """ set the database to be used """
        self.songInfoController.songInfoService.setDatabase(db)
        self.albumInfoController.albumInfoService.setDatabase(db)
        self.singerInfoController.singerInfoService.setDatabase(db)
        self.playlistController.playlistService.setDatabase(db)

    def copyTo(self, library):
        """ copy data to another library """
        library.songInfos = self.songInfos
        library.albumInfos = self.albumInfos
        library.singerInfos = self.singerInfos
        library.playlists = self.playlists
        library.recentPlaySongInfos = self.recentPlaySongInfos
        library.directories = self.directories.copy()
        library.fileSystem.setDirs(self.directories)

    def updateSongInfo(self, songInfo: SongInfo):
        """ update one song information """
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
        """ update multi song information """
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
        """ file added to file system slot """
        songInfos = self.songInfoController.addSongInfos(files)

        self.songInfos.extend(songInfos)
        self.songInfos.sort(key=lambda i: i.modifiedTime, reverse=True)
        self.albumInfos = self.albumInfoController.getAlbumInfosFromCache(
            self.songInfos)
        self.singerInfos = self.singerInfoController.getSingerInfosFromCache(
            self.albumInfos)

        self.fileAdded.emit(songInfos)

    def __onFileRemoved(self, files: List[Path]):
        """ file removed from file system slot """
        files = self.songInfoController.removeSongInfos(files)

        for songInfo in self.songInfos.copy():
            if songInfo.file in files:
                self.songInfos.remove(songInfo)

        self.albumInfos = self.albumInfoController.getAlbumInfosFromCache(
            self.songInfos)
        self.singerInfos = self.singerInfoController.getSingerInfosFromCache(
            self.albumInfos)

        self.fileRemoved.emit(files)
