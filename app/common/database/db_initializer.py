# coding:utf-8
from PyQt5.QtCore import QThread
from PyQt5.QtSql import QSqlDatabase

from .service import SongInfoService, AlbumInfoService


class DBInitializer:
    """ 数据库初始化器 """

    cacheFile = 'cache/cache.db'

    def __init__(self):
        self.connect()

    def connect(self):
        """ 连接数据库 """
        self.db = QSqlDatabase.addDatabase('QSQLITE', 'main')
        self.db.setDatabaseName(self.cacheFile)
        if not self.db.open():
            print("数据库连接失败")

    def disconnect(self):
        """ 断开连接 """
        name = self.db.connectionName()
        self.db.close()
        QSqlDatabase.removeDatabase(name)

    def init(self):
        """ 初始化数据库 """
        songInfoService = SongInfoService(self.db)
        albumInfoService = AlbumInfoService(self.db)
        songInfoService.createTable()
        albumInfoService.createTable()
