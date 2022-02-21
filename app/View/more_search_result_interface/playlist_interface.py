# coding:utf-8
from typing import List

from common.database.entity import Playlist
from common.library import Library
from components.playlist_card import GridPlaylistCardView, PlaylistCardType
from components.selection_mode_interface import (PlaylistSelectionModeInterface,
                                                 SelectionModeBarType)
from PyQt5.QtCore import QFile, QMargins, QPoint


class PlaylistInterface(PlaylistSelectionModeInterface):
    """ Playlist card interface """

    def __init__(self, library: Library, parent=None):
        super().__init__(
            library,
            GridPlaylistCardView(library, [], PlaylistCardType.PLAYLIST_CARD, margins=QMargins(15, 0, 15, 0)),
            SelectionModeBarType.PLAYLIST_CARD,
            parent
        )
        self.playlistCards = self.playlistCardView.playlistCards
        self.vBox.setContentsMargins(0, 145, 0, 120)
        self.__setQss()

    def updateWindow(self, playlists: List[Playlist]):
        """ update window """
        self.playlistCardView.updateAllCards(playlists)
        self.adjustScrollHeight()

    def __setQss(self):
        """ set style sheet """
        f = QFile(":/qss/playlist_card_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()
