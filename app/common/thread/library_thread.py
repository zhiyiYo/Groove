# coding:utf-8
from typing import List
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtSql import QSqlDatabase

from common.library import Library, Directory


class LibraryThread(QThread):
    """ Song library thread """

    reloadFinished = pyqtSignal()
    loadFromFilesFinished = pyqtSignal(list)

    def __init__(self, directories: List[Directory] = None, parent=None):
        super().__init__(parent=parent)
        db = QSqlDatabase.database('main')
        self.library = Library(directories, db, False, self)
        self.task = self.library.load
        self.params = {}
        self.taskResult = None

        self.library.reloadFinished.connect(self.reloadFinished)
        self.library.loadFromFilesFinished.connect(self.loadFromFilesFinished)

    def run(self):
        """ executive song library task """
        if not QSqlDatabase.contains('thread'):
            db = QSqlDatabase.addDatabase('QSQLITE', 'thread')
            db.setDatabaseName(Library.cacheFile)
            db.open()
            self.library.setDatabase(db)

        self.taskResult = self.task(**self.params)

    def setTask(self, task, **params):
        """ Set the song library task implemented in the thread

        Parameters
        ----------
        task:
            callable object

        **params:
            parameters to be used in the task
        """
        self.task = task
        self.params = params
