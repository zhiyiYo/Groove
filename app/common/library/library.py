# coding:utf-8
from pathlib import Path
from time import time
from typing import List

from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt5.QtSql import QSqlDatabase

from ..database.controller import (AlbumCoverController, AlbumInfoController,
                                   SongInfoController)
from .file_system import FileSystem


class Library(QObject):
    """ 歌曲库 """

    loadFinished = pyqtSignal()
    updateFinished = pyqtSignal()
    reloadFinished = pyqtSignal()

    cacheFile = 'cache/cache.db'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self, directories: List[str] = None, parent=None):
        """
        Parameters
        ----------
        directories: List[str]
            歌曲文件夹列表

        parent:
            父级
        """
        super().__init__(parent=parent)
        self.songInfos = []
        self.albumInfos = []
        self.directories = directories
        self.fileSystem = FileSystem(directories, self)
        self.songInfoController = SongInfoController()
        self.albumInfoController = AlbumInfoController()
        self.albumCoverController = AlbumCoverController()

    def load(self):
        """ 载入歌曲信息 """
        t0 = time()
        files = self.fileSystem.glob()
        t1 = time()
        print('寻找音频文件耗时：', t1 - t0)
        self.songInfos = self.songInfoController.getSongInfosFromCache(files)
        t2 = time()
        self.albumInfos = self.albumInfoController.getAlbumInfosFromCache(
            self.songInfos)
        t3 = time()
        self.albumCoverController.getAlbumCovers(self.songInfos)
        t4 = time()
        print('载入歌曲信息耗时：', t2 - t1)
        print('载入专辑信息耗时：', t3 - t2)
        print('提取专辑封面耗时：', t4 - t3)
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
        t1 = time()
        self.songInfos = self.songInfoController.getSongInfos(files)
        t2 = time()
        self.albumInfos = self.albumInfoController.getAlbumInfos(
            self.songInfos)
        t3 = time()
        self.albumCoverController.getAlbumCovers(self.songInfos)
        t4 = time()
        print('载入歌曲信息耗时：', t2 - t1)
        print('载入专辑信息耗时：', t3 - t2)
        print('提取专辑封面耗时：', t4 - t3)

        self.reloadFinished.emit()

    def moveToThread(self, thread: QThread):
        super().moveToThread(thread)

        id_ = hex(int(thread.currentThreadId()))
        if not QSqlDatabase.contains(id_):
            QSqlDatabase.addDatabase('QSQLITE', id_)

        db = QSqlDatabase.database(id_, False)
        db.setDatabaseName(self.cacheFile)
        db.open()

        self.songInfoController.songInfoService.setDatabase(db)
        self.albumInfoController.albumInfoService.setDatabase(db)
