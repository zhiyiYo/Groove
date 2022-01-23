# coding:utf-8
from pathlib import Path
from typing import List

from PyQt5.QtCore import Qt, pyqtSignal, QObject
from .file_system import FileSystem
from ..database.controller import SongInfoController


class Library(QObject):

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

    def load(self):
        """ 载入歌曲信息 """
        files = self.fileSystem.glob()
        self.songInfos = self.songInfoController.getSongInfos(files)
