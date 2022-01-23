# coding:utf-8
from pathlib import Path
from typing import List

from PyQt5.QtCore import (QDirIterator, QFileSystemWatcher, QObject, Qt,
                          QTimer, pyqtSignal, QDir)


class FileSystemWatcher(QObject):
    """ 文件系统监视器 """

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
        """ 添加一个监视的路径 """
        self.watcher.addPath(path)

    def addPaths(self, paths: List[str]):
        """ 添加多个监视的路径 """
        if not paths:
            return

        self.watcher.addPaths(paths)

    def removePath(self, path: str):
        """ 移除一个监视的路径 """
        self.watcher.removePath(path)

    def removePaths(self, paths: str):
        """ 移除多个监视的路径 """
        if not paths:
            return

        self.watcher.removePaths(paths)

    def __onDirectoryChanged(self, path: str):
        """ 文件夹改变槽函数 """
        self.changedDir = path
        self.timer.stop()
        self.timer.start(500)

    def __onTimerTimeOut(self):
        """ 定时器溢出槽函数 """
        # 文件夹又发生了变化就继续等待
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
        """ 获取文件夹大小 """
        size = 0
        iterator = QDirIterator(path, QDir.Files, QDirIterator.Subdirectories)
        while iterator.hasNext():
            iterator.next()
            size += iterator.fileInfo().size()

        return size
