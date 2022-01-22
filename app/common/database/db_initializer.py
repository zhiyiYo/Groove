# coding:utf-8
from PyQt5.QtSql import QSqlDatabase

from .service import SongInfoService


class DbInitializer:
    """ 数据库初始化器 """

    cacheFile = 'cache/cache.db'

    def __init__(self):
        self.connect()
        self.songInfoService = SongInfoService()
        self.createTables()

    def connect(self):
        """ 连接数据库 """
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.cacheFile)
        if not self.db.open():
            print("数据库连接失败")

    def createTables(self):
        """ 创建数据库表格 """
        self.songInfoService.createTable()
