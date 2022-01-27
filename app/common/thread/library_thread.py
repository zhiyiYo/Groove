# coding:utf-8
from typing import List
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtSql import QSqlDatabase

from common.library import Library, Directory


class LibraryThread(QThread):
    """ 歌曲库线程 """

    reloadFinished = pyqtSignal()

    def __init__(self, directories: List[Directory] = None, parent=None):
        super().__init__(parent=parent)
        self.db = QSqlDatabase.addDatabase('QSQLITE', 'thread')
        self.db.setDatabaseName(Library.cacheFile)
        self.db.open()
        self.library = Library(directories, self.db, self)
        self.task = self.library.load
        self.params = {}

        # 信号连接到槽
        self.library.reloadFinished.connect(self.reloadFinished)

    def run(self):
        """ 获取歌曲库信息 """
        self.task(**self.params)

    def setTask(self, task, **params):
        """ 设置任务

        Parameters
        ----------
        task:
            可调用的对象

        **params:
            函数调用时需要的参数
        """
        self.task = task
        self.params = params
