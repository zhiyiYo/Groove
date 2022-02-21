# coding:utf-8
from typing import List

from common.signal_bus import signalBus
from common.database.entity import SongInfo
from components.selection_mode_interface import (SelectionModeBarType,
                                                 SongSelectionModeInterface)
from components.song_list_widget import SongListWidget


class LocalSongInterface(SongSelectionModeInterface):
    """ Local song interface """

    def __init__(self, songInfos: List[SongInfo], parent=None):
        super().__init__(SongListWidget(songInfos), SelectionModeBarType.SONG_TAB, parent)
        self.resize(1270, 800)
        self.vBox.setContentsMargins(0, 145, 0, 0)
        self.__connectSignalToSlot()

    def updateWindow(self, songInfos: List[SongInfo]):
        """ update window """
        self.songListWidget.updateAllSongCards(songInfos)
        self.adjustScrollHeight()

    def deleteSongs(self, songPaths: List[str]):
        """ delete songs """
        self.songListWidget.removeSongCards(songPaths)
        self.adjustScrollHeight()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.songListWidget.removeSongSignal.connect(
            lambda songInfo: signalBus.removeSongSig.emit([songInfo.file]))
