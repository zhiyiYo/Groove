# coding:utf-8
from common.logger import Logger
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import qApp

from .service import (AlbumInfoService, PlaylistService, SingerInfoService,
                      SongInfoService)


class DBInitializer:
    """ Database initializer """

    logger = Logger("cache")
    connectionName = "main"
    cacheFile = 'cache/cache.db'

    @classmethod
    def init(cls):
        """ Initialize database """
        db = QSqlDatabase.addDatabase('QSQLITE', cls.connectionName)
        db.setDatabaseName(cls.cacheFile)
        if not db.open():
            Logger.error("Database connection failed")
            qApp.exit()

        SongInfoService(db).createTable()
        AlbumInfoService(db).createTable()
        SingerInfoService(db).createTable()
        PlaylistService(db).createTable()