# coding:utf-8
from common.logger import Logger
from common.cache import dbPath
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import qApp

from .service import (AlbumInfoService, PlaylistService, RecentPlayService,
                      SingerInfoService, SongInfoService)


class DBInitializer:
    """ Database initializer """

    logger = Logger("cache")
    CONNECTION_NAME = "main"
    CACHE_FILE = str(dbPath)

    @classmethod
    def init(cls):
        """ Initialize database """
        db = QSqlDatabase.addDatabase('QSQLITE', cls.CONNECTION_NAME)
        db.setDatabaseName(cls.CACHE_FILE)
        if not db.open():
            cls.logger.error("Database connection failed")
            qApp.exit()

        SongInfoService(db).createTable()
        AlbumInfoService(db).createTable()
        SingerInfoService(db).createTable()
        PlaylistService(db).createTable()
        RecentPlayService(db).createTable()