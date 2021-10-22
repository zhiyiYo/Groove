# coding:utf-8
from PyQt5.QtCore import QMargins, Qt

from .basic_song_list_widget import BasicSongListWidget
from .song_card_type import SongCardType


class NoScrollSongListWidget(BasicSongListWidget):
    """ 禁用了滚动的歌曲列表课件 """

    def __init__(self, songInfo_list: list, songCardType: SongCardType, parent=None,
                 viewportMargins=QMargins(30, 0, 30, 0), paddingBottomHeight=116):
        """
        Parameters
        ----------
        songInfo_list: list
            歌曲信息列表

        songCardType: SongCardType
            歌曲卡类型

        parent:
            父级窗口

        viewportMargins: QMargins
            视口的外边距

        paddingBottomHeight: int
            列表视图底部留白
        """
        super().__init__(songInfo_list, songCardType, parent, viewportMargins, 0)
        self.__paddingBottomHeight = paddingBottomHeight
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def wheelEvent(self, e):
        return

    def appendOneSongCard(self, songInfo: dict):
        super().appendOneSongCard(songInfo)
        self.__adjustHeight()

    def appendSongCards(self, songInfo_list: list):
        super().appendSongCards(songInfo_list)
        self.__adjustHeight()

    def updateAllSongCards(self, songInfo_list: list):
        """ 更新所有歌曲卡，根据给定的信息决定创建或者删除歌曲卡 """
        super().updateAllSongCards(songInfo_list)
        self.__adjustHeight()

    def removeSongCard(self, index):
        super().removeSongCard(index)
        self.__adjustHeight()

    def clearSongCards(self):
        super().clearSongCards()
        self.__adjustHeight()

    def __adjustHeight(self):
        """ 调整高度 """
        self.resize(self.width(), 60*len(self.songCard_list) +
                    self.__paddingBottomHeight)
