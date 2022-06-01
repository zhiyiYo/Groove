# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from PyQt5.QtCore import QMargins, Qt

from .basic_song_list_widget import BasicSongListWidget
from .song_card_type import SongCardType


class NoScrollSongListWidget(BasicSongListWidget):
    """ Song list widget which disable scrolling """

    def __init__(self, songInfos: list, songCardType: SongCardType, parent=None,
                 viewportMargins=QMargins(30, 0, 30, 0), paddingBottomHeight=116):
        """
        Parameters
        ----------
        songInfos: list
            song information list

        songCardType: SongCardType
            song card type

        parent:
            parent window

        viewportMargins: QMargins
            viewport margins

        paddingBottomHeight: int
            leave a blank at the bottom. If it is `0` or `None`, it will not be added
        """
        super().__init__(songInfos, songCardType, parent, viewportMargins, 0)
        self.resize(1150, 758)
        self.__paddingBottomHeight = paddingBottomHeight
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def wheelEvent(self, e):
        return

    def appendOneSongCard(self, songInfo: SongInfo):
        super().appendOneSongCard(songInfo)
        self.__adjustHeight()

    def prependOneSongCard(self, songInfo: SongInfo):
        super().prependOneSongCard(songInfo)
        self.__adjustHeight()

    def appendSongCards(self, songInfos: List[SongInfo]):
        super().appendSongCards(songInfos)
        self.__adjustHeight()

    def updateAllSongCards(self, songInfos: List[SongInfo]):
        super().updateAllSongCards(songInfos)
        self.__adjustHeight()

    def removeSongCard(self, index, emit=True):
        super().removeSongCard(index, emit)
        self.__adjustHeight()

    def clearSongCards(self):
        super().clearSongCards()
        self.__adjustHeight()

    def __adjustHeight(self):
        """ adjust height """
        self.resize(self.width(), 60*len(self.songCards) +
                    self.__paddingBottomHeight)
