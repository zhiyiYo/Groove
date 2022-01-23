# coding:utf-8
from pathlib import Path
from typing import Dict, List, Union

from PyQt5.QtCore import QObject, Qt, pyqtSignal

from .directory import Directory
from .file_system_watcher import FileSystemWatcher


class FileSystem(QObject):
    """ 文件系统 """

    added = pyqtSignal(list)
    removed = pyqtSignal(list)

    def __init__(self, directories: List[str] = None, parent=None):
        """
        Parameters
        ----------
        directories: List[str]
            文件夹列表

        parent:
            父级
        """
        super().__init__(parent=parent)
        self.directories = {}  # type:Dict[Path, Directory]
        self.watcher = FileSystemWatcher(self)
        self.watcher.directoryChanged.connect(self.__onDirectoryChanged)
        if directories:
            self.addDirs(directories)

    def addDir(self, path: Union[str, Path]):
        """ 添加一个文件夹 """
        if not isinstance(path, Path):
            path = Path(path)

        if path in self.directories:
            return

        self.directories[path] = Directory(path)
        self.watcher.addPath(str(path))

    def removeDir(self, path: Union[str, Path]):
        """ 移除一个文件夹 """
        if not isinstance(path, Path):
            path = Path(path)

        if path not in self.directories:
            return

        self.directories.pop(path)
        self.watcher.removePath(str(path))

    def addDirs(self, paths: List[Union[str, Path]]):
        """ 添加多个文件夹 """
        for path in paths:
            self.addDir(path)

    def removeDirs(self, paths: List[Union[str, Path]]):
        """ 移除多个文件夹 """
        for path in paths:
            self.removeDir(path)

    def glob(self):
        """ 获取所有音频文件 """
        files = []  # type:List[Path]
        for directory in self.directories.values():
            files.extend(directory.glob())

        return files

    def __onDirectoryChanged(self, path: str):
        """ 文件夹改变槽函数 """
        directory = self.directories[Path(path)]
        changedFiles = directory.update()

        if changedFiles['removed']:
            self.removed.emit(changedFiles['removed'])

        if changedFiles['added']:
            self.added.emit(changedFiles['added'])
