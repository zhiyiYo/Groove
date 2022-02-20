# coding:utf-8
from PyQt5.QtSql import QSqlDatabase

from .service import (AlbumInfoService, PlaylistService, SingerInfoService,
                      SongInfoService)


class DBInitializer:
    """ Database initializer """

    cacheFile = 'cache/cache.db'

    def __init__(self):
        self.connect()

    def connect(self):
        """ connect database """
        self.db = QSqlDatabase.addDatabase('QSQLITE', 'main')
        self.db.setDatabaseName(self.cacheFile)
        if not self.db.open():
            print("Database connection failed")

    def init(self):
        """ Initialize database """
        songInfoService = SongInfoService(self.db)
        albumInfoService = AlbumInfoService(self.db)
        singerInfoService = SingerInfoService(self.db)
        playlistService = PlaylistService(self.db)
        songInfoService.createTable()
        albumInfoService.createTable()
        singerInfoService.createTable()
        playlistService.createTable()