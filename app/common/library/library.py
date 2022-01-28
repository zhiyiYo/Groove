# coding:utf-8
from pathlib import Path
from time import time
from typing import List

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtSql import QSqlDatabase

from ..database.controller import (AlbumCoverController, AlbumInfoController,
                                   SingerInfoController, SongInfoController)
from .file_system import FileSystem


class Library(QObject):
    """ 歌曲库 """

    loadFinished = pyqtSignal()
    updateFinished = pyqtSignal()
    reloadFinished = pyqtSignal()

    cacheFile = 'cache/cache.db'

    def __init__(self, directories: List[str] = None, db: QSqlDatabase = None, parent=None):
        """
        Parameters
        ----------
        directories: List[str]
            歌曲文件夹列表

        db: QDataBase
            使用的数据库

        parent:
            父级
        """
        super().__init__(parent=parent)
        self.songInfos = []
        self.albumInfos = []
        self.directories = directories
        self.fileSystem = FileSystem(directories, self)
        self.songInfoController = SongInfoController(db)
        self.albumInfoController = AlbumInfoController(db)
        self.albumCoverController = AlbumCoverController()
        self.singerInfoController = SingerInfoController(db)

    def load(self):
        """ 载入歌曲信息 """
        files = self.fileSystem.glob()
        self.songInfos = self.songInfoController.getSongInfosFromCache(files)
        self.albumInfos = self.albumInfoController.getAlbumInfosFromCache(
            self.songInfos)
        self.albumCoverController.getAlbumCovers(self.songInfos)
        self.singerInfos = self.singerInfoController.getSingerInfosFromCache(
            self.albumInfos)

        self.loadFinished.emit()

    def setDirectories(self, directories: List[str]):
        """ 设置歌曲文件目录 """
        isChanged = self.fileSystem.setDirs(directories)

        if not isChanged:
            self.reloadFinished.emit()
            return

        self.directories = directories

        # 更新信息列表和数据库
        files = self.fileSystem.glob()
        self.songInfos = self.songInfoController.getSongInfos(files)
        self.albumInfos = self.albumInfoController.getAlbumInfos(
            self.songInfos)
        self.albumCoverController.getAlbumCovers(self.songInfos)
        self.singerInfos = self.singerInfoController.getSingerInfos(
            self.albumInfos)

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
        library.directories = self.directories.copy()
        library.fileSystem.setDirs(self.directories)
