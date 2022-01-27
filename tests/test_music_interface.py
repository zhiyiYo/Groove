# coding:utf-8
import sys

sys.path.append('app')

from time import time
from unittest import TestCase

from app.common import resource
from app.common.database.entity import SongInfo
from app.common.library import Library
from app.View.my_music_interface import MyMusicInterface
from PyQt5.QtCore import QLocale, Qt, QTranslator
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QApplication


class TestMyMusicInterface(TestCase):
    """ 测试歌曲卡 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./app/cache/cache.db')
        if not self.db.open():
            raise Exception("数据库连接失败")

        self.library = Library(['D:/hzz/Music'])

    def test_run(self):
        """ 测试运行 """
        self.library.load()

        app = QApplication(sys.argv)
        translator = QTranslator()
        translator.load(QLocale.system(), ":/i18n/Groove_")
        app.installTranslator(translator)

        w = MyMusicInterface(self.library)
        w.show()
        app.exec_()
