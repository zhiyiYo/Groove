# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtSql import QSqlDatabase


class LibraryThread(QThread):
    """ 歌曲库线程 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        id_ = hex(int(self.currentThreadId()))
        self.db = QSqlDatabase.addDatabase('QSQLITE', id_)
        self.db.setDatabaseName('cache/cache.db')
        if not self.db.open():
            raise Exception('数据库连接失败')
