# coding:utf-8
from pathlib import Path
from typing import List
from time import time

from PyQt5.QtCore import QObject, Qt, pyqtSignal

from ..database.controller import AlbumInfoController, SongInfoController
from .file_system import FileSystem


class Library(QObject):
    """ 歌曲库 """

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
        self.directories = directories
        self.fileSystem = FileSystem(directories, self)
        self.songInfoController = SongInfoController()
        self.albumInfoController = AlbumInfoController()

    def load(self):
        """ 载入歌曲信息 """
        files = self.fileSystem.glob()
        t0 = time()
        self.songInfos = self.songInfoController.getSongInfos(files)
        t1 = time()
        self.albumInfos = self.albumInfoController.getAlbumInfos(self.songInfos)
        t2 = time()
        print('载入歌曲信息耗时：', t1 - t0)
        print('载入专辑信息耗时：', t2 - t1)
