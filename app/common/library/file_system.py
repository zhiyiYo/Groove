# coding:utf-8
from pathlib import Path
from typing import Dict, List, Union

from PyQt5.QtCore import QObject, Qt, pyqtSignal

from .directory import Directory
from .file_system_watcher import FileSystemWatcher


class FileSystem(QObject):
    """ File system class """

    added = pyqtSignal(list)
    removed = pyqtSignal(list)

    def __init__(self, directories: List[str] = None, parent=None):
        """
        Parameters
        ----------
        directories: List[str]
            directory list

        parent:
            parent instance
        """
        super().__init__(parent=parent)
        self.directories = {}  # type:Dict[Path, Directory]
        self.watcher = FileSystemWatcher(self)
        self.watcher.directoryChanged.connect(self.__onDirectoryChanged)
        if directories:
            self.addDirs(directories)

    def setDirs(self, paths: List[Union[str, Path]]):
        """ Set the directories in the file system

        Parameters
        ----------
        paths: List[str | Path]
            directory list

        Returns
        -------
        isChanged: bool
            whether the directories in file system has changed
        """
        directories = set(paths)
        oldDirectories = set(self.directories.keys())

        if directories == oldDirectories:
            return False

        self.removeDirs(oldDirectories - directories)
        self.addDirs(directories - oldDirectories)
        return True

    def addDir(self, path: Union[str, Path]):
        """ add a directory to file system """
        if not isinstance(path, Path):
            path = Path(path)

        if path in self.directories:
            return

        self.directories[path] = Directory(path)
        self.watcher.addPath(str(path))

    def removeDir(self, path: Union[str, Path]):
        """ remove a directory from file system """
        if not isinstance(path, Path):
            path = Path(path)

        if path not in self.directories:
            return

        self.directories.pop(path)
        self.watcher.removePath(str(path))

    def addDirs(self, paths: List[Union[str, Path]]):
        """ add multi directories to file system """
        for path in paths:
            self.addDir(path)

    def removeDirs(self, paths: List[Union[str, Path]]):
        """ remove multi directories from file system """
        for path in paths:
            self.removeDir(path)

    def glob(self):
        """ get all audio file paths """
        files = []  # type:List[Path]
        for directory in self.directories.values():
            files.extend(directory.glob())

        return files

    def __onDirectoryChanged(self, path: str):
        """ directory changed slot """
        directory = self.directories[Path(path)]
        changedFiles = directory.update()

        if changedFiles['removed']:
            self.removed.emit(changedFiles['removed'])

        if changedFiles['added']:
            self.added.emit(changedFiles['added'])
