# coding:utf-8
from PyQt5.QtCore import QObject


class Translator(QObject):
    """ Common translator """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hrs = self.tr("hrs")
        self.mins = self.tr('mins')
        self.unknownGenre = self.tr("Unknown genre")
        self.unknownArtist = self.tr("Unknown artist")

