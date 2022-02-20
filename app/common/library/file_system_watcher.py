# coding:utf-8
from typing import List

from PyQt5.QtCore import (QDir, QDirIterator, QFileSystemWatcher, QObject,
                          QTimer, pyqtSignal)


class FileSystemWatcher(QObject):
    """ File system watcher class """

    directoryChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.watcher = QFileSystemWatcher(self)
        self.timer = QTimer(self)
        self.lastDirSize = 0
        self.changedDir = ''

        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.__onTimerTimeOut)
        self.watcher.directoryChanged.connect(self.__onDirectoryChanged)

    def addPath(self, path: str):
        """ add a monitored path """
        self.watcher.addPath(path)

    def addPaths(self, paths: List[str]):
        """ add multi monitored paths """
        if not paths:
            return

        self.watcher.addPaths(paths)

    def removePath(self, path: str):
        """ remove a monitored path """
        self.watcher.removePath(path)

    def removePaths(self, paths: str):
        """ remove multi monitored paths """
        if not paths:
            return

        self.watcher.removePaths(paths)

    def __onDirectoryChanged(self, path: str):
        """ directory changed slot """
        self.changedDir = path
        self.timer.stop()
        self.timer.start(500)

    def __onTimerTimeOut(self):
        """ timer time out slot """
        # wait until the folder no longer changes
        size = self.getDirSize(self.changedDir)
        if self.lastDirSize != size:
            self.lastDirSize = size
            self.timer.start(500)
            return

        self.directoryChanged.emit(self.changedDir)
        self.lastDirSize = 0
        self.changedDir = ''

    @staticmethod
    def getDirSize(path: str):
        """ get directory size """
        size = 0
        iterator = QDirIterator(path, QDir.Files, QDirIterator.Subdirectories)
        while iterator.hasNext():
            iterator.next()
            size += iterator.fileInfo().size()

        return size
